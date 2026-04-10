"""Integration tests for the FastAPI application."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_api_app
from src.domain.actions import Action
from src.domain.models import TelemetrySnapshot
from src.services.profile_service import ProfileService
from src.services.telemetry_service import TelemetryService
from src.utils.config import load_config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_client(
    tmp_path: Path,
    api_key: str = "",
) -> tuple[TestClient, ProfileService, TelemetryService]:
    config = load_config(project_root=tmp_path)
    # Override api_key via object attribute (config is a dataclass)
    object.__setattr__(config, "api_key", api_key)
    profile_service = ProfileService(config.profiles_dir, config.active_profile_file)
    telemetry_service = TelemetryService(config.telemetry_file)
    app = create_api_app(
        config=config,
        profile_service=profile_service,
        telemetry_service=telemetry_service,
    )
    return TestClient(app), profile_service, telemetry_service


def _snap(action: Action = Action.CENTER, fps: int = 30) -> TelemetrySnapshot:
    return TelemetrySnapshot(action=action, fps=fps, has_hand=True, profile="default", center_x=0.5)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health_returns_ok(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path)
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body


# ---------------------------------------------------------------------------
# Profile CRUD
# ---------------------------------------------------------------------------


def test_list_profiles_contains_default(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path)
    response = client.get("/v1/profiles")
    assert response.status_code == 200
    data = response.json()
    assert "active" in data
    names = [p["name"] for p in data["items"]]
    assert "default" in names


def test_create_and_retrieve_profile(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path)
    payload = {
        "description": "Night setup",
        "left_bound": 0.31,
        "right_bound": 0.69,
        "detection_confidence": 0.72,
        "presence_confidence": 0.72,
        "tracking_confidence": 0.61,
        "cooldown_ms": 210,
    }
    save_resp = client.put("/v1/profiles/night_mode", json=payload)
    assert save_resp.status_code == 200
    assert save_resp.json()["status"] == "saved"

    get_resp = client.get("/v1/profiles/night_mode")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "night_mode"
    assert get_resp.json()["cooldown_ms"] == 210


def test_activate_profile(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path)
    client.put(
        "/v1/profiles/second", json={"description": "second", "left_bound": 0.3, "right_bound": 0.7}
    )
    act_resp = client.post("/v1/profiles/second/activate")
    assert act_resp.status_code == 200
    assert act_resp.json()["status"] == "activated"

    list_resp = client.get("/v1/profiles")
    assert list_resp.json()["active"] == "second"


def test_get_unknown_profile_returns_404(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path)
    response = client.get("/v1/profiles/nonexistent")
    assert response.status_code == 404


def test_create_profile_with_inverted_bounds_returns_422(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path)
    payload = {"left_bound": 0.80, "right_bound": 0.20}
    response = client.put("/v1/profiles/bad", json=payload)
    assert response.status_code == 422


def test_create_profile_with_equal_bounds_returns_422(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path)
    payload = {"left_bound": 0.50, "right_bound": 0.50}
    response = client.put("/v1/profiles/bad2", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------


def test_telemetry_returns_null_latest_when_empty(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path)
    response = client.get("/v1/telemetry")
    assert response.status_code == 200
    assert response.json()["latest"] is None


def test_telemetry_returns_published_snapshot(tmp_path: Path) -> None:
    client, _, telemetry = _build_client(tmp_path)
    telemetry.publish(_snap(Action.LEFT, fps=48))

    response = client.get("/v1/telemetry?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["latest"]["action"] == "LEFT"
    assert data["history"][-1]["fps"] == 48


# ---------------------------------------------------------------------------
# API key authentication
# ---------------------------------------------------------------------------


def test_protected_endpoint_without_key_returns_401(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path, api_key="secret123")
    response = client.get("/v1/profiles")
    assert response.status_code == 401


def test_protected_endpoint_with_correct_key_succeeds(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path, api_key="secret123")
    response = client.get("/v1/profiles", headers={"x-api-key": "secret123"})
    assert response.status_code == 200


def test_protected_endpoint_with_wrong_key_returns_401(tmp_path: Path) -> None:
    client, _, _ = _build_client(tmp_path, api_key="secret123")
    response = client.get("/v1/profiles", headers={"x-api-key": "wrong"})
    assert response.status_code == 401


def test_health_is_public_regardless_of_api_key(tmp_path: Path) -> None:
    """Health check must be reachable without authentication."""
    client, _, _ = _build_client(tmp_path, api_key="secret123")
    response = client.get("/v1/health")
    assert response.status_code == 200
