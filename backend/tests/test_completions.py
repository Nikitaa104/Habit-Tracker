from datetime import date, timedelta
import pytest


def _make_habit(client, name="Exercise"):
    return client.post("/api/habits", json={"name": name}).json


def test_log_completion_today(client):
    habit = _make_habit(client)
    resp = client.post(f"/api/habits/{habit['id']}/completions", json={})
    assert resp.status_code == 201
    assert resp.json["completed_on"] == date.today().isoformat()


def test_log_completion_with_note(client):
    habit = _make_habit(client)
    resp = client.post(f"/api/habits/{habit['id']}/completions", json={"note": "Felt great!"})
    assert resp.status_code == 201
    assert resp.json["note"] == "Felt great!"


def test_log_completion_custom_date(client):
    habit = _make_habit(client)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = client.post(f"/api/habits/{habit['id']}/completions", json={"completed_on": yesterday})
    assert resp.status_code == 201
    assert resp.json["completed_on"] == yesterday


def test_log_completion_future_date_rejected(client):
    habit = _make_habit(client)
    future = (date.today() + timedelta(days=1)).isoformat()
    resp = client.post(f"/api/habits/{habit['id']}/completions", json={"completed_on": future})
    assert resp.status_code == 422


def test_duplicate_completion_rejected(client):
    habit = _make_habit(client)
    client.post(f"/api/habits/{habit['id']}/completions", json={})
    resp = client.post(f"/api/habits/{habit['id']}/completions", json={})
    assert resp.status_code == 409
    assert "already logged" in resp.json["error"]


def test_completion_reflects_in_habit(client):
    habit = _make_habit(client)
    client.post(f"/api/habits/{habit['id']}/completions", json={})
    updated = client.get(f"/api/habits/{habit['id']}").json
    assert updated["completed_today"] is True


def test_undo_completion(client):
    habit = _make_habit(client)
    client.post(f"/api/habits/{habit['id']}/completions", json={})
    today = date.today().isoformat()
    resp = client.delete(f"/api/habits/{habit['id']}/completions/{today}")
    assert resp.status_code == 204
    updated = client.get(f"/api/habits/{habit['id']}").json
    assert updated["completed_today"] is False


def test_undo_completion_idempotent(client):
    """Undoing a completion that does not exist should not error."""
    habit = _make_habit(client)
    today = date.today().isoformat()
    resp = client.delete(f"/api/habits/{habit['id']}/completions/{today}")
    assert resp.status_code == 204


def test_undo_completion_bad_date_format(client):
    habit = _make_habit(client)
    resp = client.delete(f"/api/habits/{habit['id']}/completions/not-a-date")
    assert resp.status_code == 400


def test_list_completions(client):
    habit = _make_habit(client)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    client.post(f"/api/habits/{habit['id']}/completions", json={"completed_on": yesterday})
    client.post(f"/api/habits/{habit['id']}/completions", json={})
    resp = client.get(f"/api/habits/{habit['id']}/completions")
    assert resp.status_code == 200
    assert len(resp.json) == 2


def test_completion_on_deleted_habit_returns_404(client):
    habit = _make_habit(client)
    client.delete(f"/api/habits/{habit['id']}")
    resp = client.post(f"/api/habits/{habit['id']}/completions", json={})
    assert resp.status_code == 404
