import pytest


def test_list_habits_empty(client):
    resp = client.get("/api/habits")
    assert resp.status_code == 200
    assert resp.json == []


def test_create_habit_success(client):
    resp = client.post("/api/habits", json={
        "name": "Drink water",
        "frequency": "daily",
        "color": "#22c55e"
    })
    assert resp.status_code == 201
    data = resp.json
    assert data["name"] == "Drink water"
    assert data["frequency"] == "daily"
    assert data["streak"] == 0
    assert data["completed_today"] is False


def test_create_habit_missing_name(client):
    resp = client.post("/api/habits", json={"frequency": "daily"})
    assert resp.status_code == 422
    assert "name" in resp.json["errors"]


def test_create_habit_invalid_color(client):
    resp = client.post("/api/habits", json={"name": "X", "color": "red"})
    assert resp.status_code == 422
    assert "color" in resp.json["errors"]


def test_create_habit_invalid_frequency(client):
    resp = client.post("/api/habits", json={"name": "X", "frequency": "hourly"})
    assert resp.status_code == 422


def test_create_habit_name_stripped(client):
    resp = client.post("/api/habits", json={"name": "  Run  "})
    assert resp.status_code == 201
    assert resp.json["name"] == "Run"


def test_get_habit(client):
    created = client.post("/api/habits", json={"name": "Meditate"}).json
    resp = client.get(f"/api/habits/{created['id']}")
    assert resp.status_code == 200
    assert resp.json["id"] == created["id"]


def test_get_habit_not_found(client):
    resp = client.get("/api/habits/9999")
    assert resp.status_code == 404


def test_update_habit(client):
    created = client.post("/api/habits", json={"name": "Read"}).json
    resp = client.patch(f"/api/habits/{created['id']}", json={"name": "Read books"})
    assert resp.status_code == 200
    assert resp.json["name"] == "Read books"


def test_archive_habit(client):
    created = client.post("/api/habits", json={"name": "Stretch"}).json
    client.patch(f"/api/habits/{created['id']}", json={"archived": True})

    # Archived habit should NOT appear in default list
    habits = client.get("/api/habits").json
    assert all(h["id"] != created["id"] for h in habits)

    # But should appear when explicitly requested
    habits_with_archived = client.get("/api/habits?archived=true").json
    assert any(h["id"] == created["id"] for h in habits_with_archived)


def test_delete_habit(client):
    created = client.post("/api/habits", json={"name": "Journal"}).json
    resp = client.delete(f"/api/habits/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/api/habits/{created['id']}").status_code == 404


def test_list_habits_excludes_archived_by_default(client):
    client.post("/api/habits", json={"name": "Active"})
    archived = client.post("/api/habits", json={"name": "Old"}).json
    client.patch(f"/api/habits/{archived['id']}", json={"archived": True})

    habits = client.get("/api/habits").json
    assert len(habits) == 1
    assert habits[0]["name"] == "Active"
