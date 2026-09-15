import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, engine, get_db
from app.core.redis_client import get_redis
from app.main import app


@pytest.fixture()
def db_session():
    """A session scoped to a SAVEPOINT so app-code `commit()` calls during a
    test never escape the outer transaction, which is always rolled back."""
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = session_factory()
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def _ensure_schema():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def _clean_llm_provider_state():
    """The LLM router's provider-availability flags live in real Redis, not
    the per-test DB transaction, so they'd otherwise leak between tests."""
    redis_client = get_redis()
    redis_client.delete("llm:groq:unavailable", "llm:gemini:unavailable")
    yield
    redis_client.delete("llm:groq:unavailable", "llm:gemini:unavailable")
