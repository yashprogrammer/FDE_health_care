"""One-time database setup done by hospital IT (DBA rights): roles and schemas for MediTrack.

  meditrack  login, owns schema "meditrack" (the application's tables)
  mis        schema of read-only reporting views (created by IT in 2019 for the MIS team)
  mis_ro     group role: SELECT on the mis views, nothing else
  mis_report login in mis_ro, used for MIS exports (e.g. the POC's de-identified extract)

Idempotent. Usage: DB_ADMIN_URL=postgresql://admin:...@host/citycare python -m legacy_meditrack.backend.bootstrap
"""
import os

import psycopg
from psycopg import sql


def ensure_login(c: psycopg.Connection, role: str, password: str) -> None:
    exists = c.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)).fetchone()
    verb = "ALTER" if exists else "CREATE"
    c.execute(sql.SQL(verb + " ROLE {} LOGIN PASSWORD {}").format(sql.Identifier(role), sql.Literal(password)))


def ensure_group(c: psycopg.Connection, role: str) -> None:
    if not c.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)).fetchone():
        c.execute(sql.SQL("CREATE ROLE {} NOLOGIN").format(sql.Identifier(role)))


def grant_role(c: psycopg.Connection, role: str, to: str) -> None:
    c.execute(sql.SQL("GRANT {} TO {}").format(sql.Identifier(role), sql.Identifier(to)))


def main() -> None:
    admin_url = os.environ["DB_ADMIN_URL"]
    db = psycopg.conninfo.conninfo_to_dict(admin_url)["dbname"]
    with psycopg.connect(admin_url, autocommit=True) as c:
        ensure_login(c, "meditrack", os.getenv("MEDITRACK_DB_PASSWORD", "meditrack"))
        ensure_login(c, "mis_report", os.getenv("MIS_DB_PASSWORD", "mis_report"))
        ensure_group(c, "mis_ro")
        grant_role(c, "mis_ro", "mis_report")
        # Azure's admin is not a superuser: it must be a member of a role to create objects owned by it
        grant_role(c, "meditrack", c.info.user)

        c.execute("CREATE SCHEMA IF NOT EXISTS meditrack AUTHORIZATION meditrack")
        c.execute("CREATE SCHEMA IF NOT EXISTS mis AUTHORIZATION meditrack")
        c.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(sql.Identifier(db)))
        for r in ("meditrack", "mis_ro"):
            c.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(sql.Identifier(db), sql.Identifier(r)))
        c.execute("ALTER ROLE meditrack SET search_path = meditrack")
        c.execute("ALTER ROLE mis_report SET search_path = mis")
        c.execute("GRANT USAGE ON SCHEMA mis TO mis_ro")
        # views are recreated on every reseed; this keeps mis_ro's SELECT on them
        c.execute("ALTER DEFAULT PRIVILEGES FOR ROLE meditrack IN SCHEMA mis GRANT SELECT ON TABLES TO mis_ro")
        c.execute("GRANT SELECT ON ALL TABLES IN SCHEMA mis TO mis_ro")
    print("MediTrack roles and schemas ready (meditrack, mis, mis_ro, mis_report)")


if __name__ == "__main__":
    main()
