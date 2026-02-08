from fastapi.testclient import TestClient

from src.api.app import create_api_app
from src.domain.actions import Action
from src.domain.models import TelemetrySnapshot
from src.services.profile_service import ProfileService
from src.services.telemetry_service import TelemetryService
from src.utils.config import load_config


def build_client(tmp_path):
    config = load_config(project_root=tmp_path)
    profile_service = ProfileService(config.profiles_dir, config.active_profile_file)
    telemetry_service = TelemetryService(config.telemetry_file)
    app = create_api_app(
        config=config,
        profile_service=profile_service,
        telemetry_service=telemetry_service,
    )
    return TestClient(app), telemetry_service


def test_health_endpoint(tmp_path):
    client, _ = build_client(tmp_path)
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_profile_creation_and_activation(tmp_path):
    client, _ = build_client(tmp_path)
    payload = {
        "description": "Night setup",
        "left_bound": 0.31,
        "right_bound": 0.69,
        "detection_confidence": 0.72,
        "presence_confidence": 0.72,
        "tracking_confidence": 0.61,
        "cooldown_ms": 210,
    }

    save_response = client.put("/v1/profiles/night_mode", json=payload)
    assert save_response.status_code == 200
    activate_response = client.post("/v1/profiles/night_mode/activate")
    assert activate_response.status_code == 200
    list_response = client.get("/v1/profiles")
    assert list_response.json()["active"] == "night_mode"


def test_telemetry_endpoint_returns_latest(tmp_path):
    client, telemetry_service = build_client(tmp_path)
    telemetry_service.publish(
        TelemetrySnapshot(
            action=Action.LEFT,
            fps=48,
            has_hand=True,
            profile="default",
            center_x=0.21,
        )
    )

    response = client.get("/v1/telemetry?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["latest"]["action"] == "LEFT"
    assert data["history"][-1]["fps"] == 48

