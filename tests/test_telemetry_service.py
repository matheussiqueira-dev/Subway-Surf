"""Unit tests for TelemetryService."""

from __future__ import annotations

from pathlib import Path

from src.domain.actions import Action
from src.domain.models import TelemetrySnapshot
from src.services.telemetry_service import TelemetryService


def _snap(
    action: Action = Action.CENTER, fps: int = 30, profile: str = "default"
) -> TelemetrySnapshot:
    return TelemetrySnapshot(action=action, fps=fps, has_hand=True, profile=profile, center_x=0.5)


# ---------------------------------------------------------------------------
# Basics
# ---------------------------------------------------------------------------


def test_latest_is_none_before_publish(telemetry_service: TelemetryService) -> None:
    assert telemetry_service.latest() is None


def test_publish_updates_latest(telemetry_service: TelemetryService) -> None:
    snap = _snap(Action.JUMP, fps=60)
    telemetry_service.publish(snap)
    assert telemetry_service.latest() is snap


def test_history_grows_on_publish(telemetry_service: TelemetryService) -> None:
    for i in range(5):
        telemetry_service.publish(_snap(fps=i))
    assert len(telemetry_service.history(limit=10)) == 5


def test_history_limit_is_respected(telemetry_service: TelemetryService) -> None:
    for i in range(10):
        telemetry_service.publish(_snap(fps=i))
    assert len(telemetry_service.history(limit=3)) == 3


def test_history_returns_most_recent_entries(telemetry_service: TelemetryService) -> None:
    for fps in range(10):
        telemetry_service.publish(_snap(fps=fps))
    recent = telemetry_service.history(limit=3)
    assert [e["fps"] for e in recent] == [7, 8, 9]


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_history_persists_to_disk(tmp_path: Path) -> None:
    svc = TelemetryService(telemetry_file=tmp_path / "t.json")
    svc.publish(_snap(Action.LEFT, fps=42))
    # Create a new instance pointing at the same file.
    svc2 = TelemetryService(telemetry_file=tmp_path / "t.json")
    history = svc2.history(limit=5)
    assert len(history) == 1
    assert history[0]["fps"] == 42


# ---------------------------------------------------------------------------
# Max-history trimming
# ---------------------------------------------------------------------------


def test_max_history_caps_stored_entries(tmp_path: Path) -> None:
    svc = TelemetryService(telemetry_file=tmp_path / "t.json", max_history=5)
    for i in range(10):
        svc.publish(_snap(fps=i))
    history = svc.history(limit=100)
    assert len(history) == 5
    # Oldest entries were evicted; only the last 5 remain.
    assert history[0]["fps"] == 5


# ---------------------------------------------------------------------------
# Corrupt file resilience
# ---------------------------------------------------------------------------


def test_corrupt_file_does_not_raise(tmp_path: Path) -> None:
    telemetry_file = tmp_path / "t.json"
    telemetry_file.write_text("this is not json", encoding="utf-8")
    svc = TelemetryService(telemetry_file=telemetry_file)
    # publish should succeed by starting with an empty history.
    svc.publish(_snap())
    assert len(svc.history()) == 1
