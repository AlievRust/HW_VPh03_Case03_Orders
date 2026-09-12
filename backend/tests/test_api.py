from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.lead import Lead


class FakeQuery:
    def __init__(self, lead: Lead):
        self.lead = lead

    def options(self, *_args):
        return self

    def offset(self, *_args):
        return self

    def limit(self, *_args):
        return self

    def all(self):
        return [self.lead]


class FakeSession:
    def __init__(self):
        self.lead = Lead(
            id=1,
            first_name="Иван",
            last_name="Иванов",
            contact_value="ivan@example.com",
            business_niche="IT",
            company_size="1-10",
            task_volume="Сайт",
            budget="100000",
            result_deadline="1 месяц",
            customer_role="Руководитель",
            task_type="Разработка",
            product_interest="Backend",
            contact_method="Email",
            preferred_time="Днём",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    def query(self, _model):
        return FakeQuery(self.lead)

    def get(self, _model, _lead_id, options=None):
        return self.lead

    def execute(self, _query):
        return None

    def close(self):
        pass


def override_db():
    yield FakeSession()


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_lead_list_uses_router():
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            response = client.get("/api/leads")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["first_name"] == "Иван"


def test_invalid_admin_budget_range():
    with TestClient(app) as client:
        response = client.post(
            "/api/admin-settings",
            json={
                "service_name": "Сайт",
                "budget_min": 200,
                "budget_max": 100,
                "budget_step": 10,
            },
        )
    assert response.status_code == 422
