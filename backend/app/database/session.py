from sqlalchemy import create_engine, delete, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Alert, PriceCheck, now


def database(url):
    options = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
    if url.endswith(":memory:"):
        options["poolclass"] = StaticPool
    engine = create_engine(url, **options)
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def sqlite_options(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA busy_timeout=5000")

    return engine, sessionmaker(engine, expire_on_commit=False)


def purge_expired(session):
    timestamp = now()
    session.execute(delete(PriceCheck).where(PriceCheck.expires_at <= timestamp))
    session.execute(delete(Alert).where(Alert.expires_at <= timestamp))
    session.commit()
