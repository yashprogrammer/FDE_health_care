"""Hospital IT's one-time grant for the Discharge Copilot (DBA rights). Run after MediTrack's bootstrap.

  copilot_svc  login; member of mis_ro (SELECT on the mis reporting views only); owns schema "copilot"
               for its own drafts and audit events. No rights on MediTrack's own tables.

Idempotent. Usage: DB_ADMIN_URL=postgresql://admin:...@host/citycare python -m copilot.bootstrap
"""
import os

import psycopg
from psycopg import sql



def ensure_login(c: psycopg.Connection, role: str, password: str) -> None:
    exists = c.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)).fetchone()
    verb = "ALTER" if exists else "CREATE"
    c.execute(sql.SQL(verb + " ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(role), sql.Literal(password)))


def grant_role(c: psycopg.Connection, role: str, to: str) -> None:
    c.execute(sql.SQL("GRANT {} TO {}").format(sql.Identifier(role), sql.Identifier(to)))


def main() -> None:
    admin_url = os.environ["DB_ADMIN_URL"]
    with psycopg.connect(admin_url, autocommit=True) as c:
        ensure_login(c, "copilot_svc", os.getenv("COPILOT_DB_PASSWORD", "copilot_svc"))
        grant_role(c, "mis_ro", "copilot_svc")
        grant_role(c, "copilot_svc", c.info.user)   # Azure admin is not a superuser
        c.execute("CREATE SCHEMA IF NOT EXISTS copilot AUTHORIZATION copilot_svc")
        c.execute("ALTER ROLE copilot_svc SET search_path = copilot, mis")
        db = psycopg.conninfo.conninfo_to_dict(admin_url)["dbname"]
        c.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO copilot_svc").format(sql.Identifier(db)))
    print("Copilot login ready (copilot_svc: mis_ro + own schema copilot)")


if __name__ == "__main__":
    main()
