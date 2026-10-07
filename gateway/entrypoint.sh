#!/bin/sh
# Renders the Caddyfile from env, then starts Caddy.
#   MEDITRACK_UPSTREAM / COPILOT_UPSTREAM  where the two apps listen (compose service or Container App name)
#   DEMO_PASSWORD                          optional: protect everything with basic auth (user: DEMO_USER, default "citycare")
set -e
MEDITRACK_UPSTREAM=${MEDITRACK_UPSTREAM:-http://meditrack:8001}
COPILOT_UPSTREAM=${COPILOT_UPSTREAM:-http://copilot:8002}

AUTH=""
if [ -n "$DEMO_PASSWORD" ]; then
  HASH=$(caddy hash-password --plaintext "$DEMO_PASSWORD")
  AUTH="basic_auth {
		${DEMO_USER:-citycare} $HASH
	}"
fi

cat > /etc/caddy/Caddyfile <<CADDY
{
	admin off
	auto_https off
}

:80 {
	$AUTH

	redir /copilot /copilot/ 308

	# Discharge Copilot (internal-only app); prefix stripped. Host rewritten so Container Apps' internal ingress routes it.
	handle_path /copilot/* {
		reverse_proxy $COPILOT_UPSTREAM {
			header_up Host {upstream_hostport}
		}
	}

	# MediTrack HMS
	handle {
		reverse_proxy $MEDITRACK_UPSTREAM {
			header_up Host {upstream_hostport}
		}
	}
}
CADDY

exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
