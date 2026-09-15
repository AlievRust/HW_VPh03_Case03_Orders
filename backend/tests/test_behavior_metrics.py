import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.main import app
from app.models.behavior_metric import BehaviorMetric, BehaviorMetricCRUD

# SQLite in-memory: тесты CRUD и upsert не должны трогать реальный PostgreSQL.
# StaticPool нужен, потому что TestClient выполняет запросы в отдельном потоке,
# а без него каждое соединение получает свою пустую in-memory базу.
# Создаём только таблицу behavior_metrics: полная схема содержит JSONB
# (lead_analytics), который SQLite не умеет компилировать.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture()
def db_session():
    BehaviorMetric.__table__.create(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        BehaviorMetric.__table__.drop(bind=engine)


def override_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def payload(session_id="test-session-0001", time_on_page=5):
    return {
        "session_id": session_id,
        "application_id": 0,
        "time_on_page": time_on_page,
        "buttons_clicked": json.dumps({"Рассчитать обслуживание": 2}),
        "cursor_positions": json.dumps([{"x": 12.5, "y": 40.0}]),
        "return_frequency": 0,
    }


def test_upsert_updates_same_session(db_session):
    first = BehaviorMetricCRUD.upsert(db_session, payload(time_on_page=3))
    BehaviorMetricCRUD.upsert(db_session, payload(time_on_page=10))

    assert BehaviorMetricCRUD.count(db_session) == 1
    assert first.time_on_page == 10  # refresh в upsert подтянул обновление


def test_upsert_creates_new_sessions(db_session):
    BehaviorMetricCRUD.upsert(db_session, payload("test-session-0001", 3))
    BehaviorMetricCRUD.upsert(db_session, payload("test-session-0002", 7))

    assert BehaviorMetricCRUD.count(db_session) == 2


def test_period_stats_aggregates(db_session):
    BehaviorMetricCRUD.upsert(db_session, payload("test-session-0001", 10))
    BehaviorMetricCRUD.upsert(db_session, payload("test-session-0002", 40))
    BehaviorMetricCRUD.upsert(db_session, payload("test-session-0003", 90))

    stats = BehaviorMetricCRUD.period_stats(db_session, days=1)

    assert stats["sessions"] == 3
    assert stats["avg_time_on_page"] == 47
    assert stats["max_time_on_page"] == 90


def test_cursor_points_filters_broken_data(db_session):
    BehaviorMetricCRUD.upsert(
        db_session,
        {
            **payload("test-session-0001"),
            "cursor_positions": json.dumps(
                [{"x": 10, "y": 20}, {"x": 999, "y": 5}, "not-a-point", {"y": 7}]
            ),
        },
    )
    BehaviorMetricCRUD.upsert(
        db_session,
        {**payload("test-session-0002"), "cursor_positions": "{broken json"},
    )

    points = BehaviorMetricCRUD.cursor_points(db_session)

    assert points == [{"x": 10.0, "y": 20.0}]


def test_stats_requires_admin_token():
    # TestClient без context manager: lifespan с create_tables() не запускается,
    # поэтому тест не пытается подключиться к PostgreSQL.
    client = TestClient(app)
    response = client.get("/api/behavior-metrics/stats")

    assert response.status_code == 401


def test_submit_metrics_is_public_and_upserts(db_session):
    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app)
        first = client.post("/api/behavior-metrics/", json=payload(time_on_page=3))
        second = client.post("/api/behavior-metrics/", json=payload(time_on_page=9))

        assert first.status_code == 200
        assert first.json() == {"status": "ok"}
        assert second.status_code == 200
    finally:
        app.dependency_overrides.clear()

    assert BehaviorMetricCRUD.count(db_session) == 1
    assert db_session.get(BehaviorMetric, 1).time_on_page == 9


def test_submit_rejects_short_session_id():
    client = TestClient(app)
    response = client.post(
        "/api/behavior-metrics/",
        json={**payload(), "session_id": "short"},
    )

    assert response.status_code == 422
