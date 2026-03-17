from tests.conftest import auth_header
from app.models.incident import CallStatus


class TestIncidentCRUD:
    def test_create_incident(self, client, operator_token):
        res = client.post("/api/v1/incidents", json={
            "type": "Incendio", "location": "Andorra la Vella",
            "description": "Foc a un edifici", "priority": 3,
        }, headers=auth_header(operator_token))
        assert res.status_code == 201
        data = res.json()
        assert data["type"] == "Incendio"
        assert data["call_status"] == "en_curs"

    def test_create_without_auth(self, client):
        res = client.post("/api/v1/incidents", json={
            "type": "Incendio", "location": "X", "description": "Y", "priority": 1,
        })
        assert res.status_code in (401, 403)

    def test_create_requires_type_without_scenario(self, client, operator_token):
        res = client.post("/api/v1/incidents", json={
            "priority": 1,
        }, headers=auth_header(operator_token))
        assert res.status_code == 422

    def test_list_incidents(self, client, operator_token):
        client.post("/api/v1/incidents", json={
            "type": "Incendio", "location": "A", "description": "B", "priority": 1,
        }, headers=auth_header(operator_token))
        res = client.get("/api/v1/incidents", headers=auth_header(operator_token))
        assert res.status_code == 200
        assert len(res.json()) >= 1

    def test_list_with_pagination(self, client, operator_token):
        h = auth_header(operator_token)
        for i in range(3):
            client.post("/api/v1/incidents", json={
                "type": "Incendio", "location": f"Loc{i}", "description": "D", "priority": 1,
            }, headers=h)
        res = client.get("/api/v1/incidents?skip=1&limit=1", headers=h)
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_end_call(self, client, operator_token):
        h = auth_header(operator_token)
        inc = client.post("/api/v1/incidents", json={
            "type": "Incendio", "location": "A", "description": "B", "priority": 1,
        }, headers=h).json()
        res = client.patch(f"/api/v1/incidents/{inc['id']}/call", headers=h)
        assert res.status_code == 200
        assert res.json()["call_status"] == "finalitzada"

    def test_end_call_twice_409(self, client, operator_token):
        h = auth_header(operator_token)
        inc = client.post("/api/v1/incidents", json={
            "type": "Incendio", "location": "A", "description": "B", "priority": 1,
        }, headers=h).json()
        client.patch(f"/api/v1/incidents/{inc['id']}/call", headers=h)
        res = client.patch(f"/api/v1/incidents/{inc['id']}/call", headers=h)
        assert res.status_code == 409


class TestCascadeDelete:
    def test_delete_incident_cascades(self, client, operator_token, session):
        h = auth_header(operator_token)
        inc = client.post("/api/v1/incidents", json={
            "type": "Incendio", "location": "A", "description": "B", "priority": 1,
        }, headers=h).json()
        inc_id = inc["id"]

        # Add intervention
        client.post("/api/v1/interventions", json={
            "incident_id": inc_id, "exact_address": "Carrer 1",
        }, headers=h)

        # Delete incident — should cascade
        res = client.delete(f"/api/v1/incidents/{inc_id}", headers=h)
        assert res.status_code == 204

        # Verify cascade
        assert client.get(f"/api/v1/incidents/{inc_id}", headers=h).status_code == 404
        assert client.get(f"/api/v1/interventions/{inc_id}", headers=h).status_code == 404
