"""Unit tests for domain models (Profile, GestureSnapshot, TelemetrySnapshot)."""

from __future__ import annotations

import pytest

from src.domain.actions import Action, parse_action
from src.domain.models import GestureSnapshot, Profile, TelemetrySnapshot


# ---------------------------------------------------------------------------
# Action / parse_action
# ---------------------------------------------------------------------------

class TestParseAction:
    def test_valid_uppercase(self) -> None:
        assert parse_action("JUMP") == Action.JUMP

    def test_valid_lowercase(self) -> None:
        assert parse_action("slide") == Action.SLIDE

    def test_unknown_falls_back_to_idle(self) -> None:
        assert parse_action("UNKNOWN") == Action.IDLE

    def test_empty_string_falls_back_to_idle(self) -> None:
        assert parse_action("") == Action.IDLE

    def test_action_passthrough(self) -> None:
        assert parse_action(Action.RIGHT) == Action.RIGHT


# ---------------------------------------------------------------------------
# Profile validation
# ---------------------------------------------------------------------------

class TestProfile:
    def test_valid_profile_passes(self) -> None:
        p = Profile(name="test_profile")
        p.validate()  # should not raise

    def test_invalid_name_raises(self) -> None:
        p = Profile(name="invalid name!")
        with pytest.raises(ValueError, match="Profile name"):
            p.validate()

    def test_bounds_inversion_raises(self) -> None:
        p = Profile(name="x", left_bound=0.70, right_bound=0.30)
        with pytest.raises(ValueError, match="boundaries"):
            p.validate()

    def test_equal_bounds_raise(self) -> None:
        p = Profile(name="x", left_bound=0.50, right_bound=0.50)
        with pytest.raises(ValueError):
            p.validate()

    def test_confidence_out_of_range_raises(self) -> None:
        p = Profile(name="x", detection_confidence=1.5)
        with pytest.raises(ValueError, match="detection_confidence"):
            p.validate()

    def test_cooldown_too_low_raises(self) -> None:
        p = Profile(name="x", cooldown_ms=10)
        with pytest.raises(ValueError, match="cooldown_ms"):
            p.validate()

    def test_round_trip_serialisation(self) -> None:
        original = Profile(
            name="competitive",
            description="Low latency",
            left_bound=0.30,
            right_bound=0.70,
            cooldown_ms=180,
        )
        restored = Profile.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.cooldown_ms == original.cooldown_ms
        assert restored.left_bound == original.left_bound

    def test_from_dict_rejects_invalid_data(self) -> None:
        with pytest.raises(ValueError):
            Profile.from_dict({"name": "bad bounds", "left_bound": 0.8, "right_bound": 0.2})


# ---------------------------------------------------------------------------
# GestureSnapshot
# ---------------------------------------------------------------------------

class TestGestureSnapshot:
    def test_default_values(self) -> None:
        snap = GestureSnapshot()
        assert snap.action == Action.IDLE
        assert snap.has_hand is False
        assert snap.center_x == 0.5
        assert snap.fingers == [False] * 5

    def test_to_dict_contains_all_keys(self) -> None:
        snap = GestureSnapshot(action=Action.JUMP, has_hand=True)
        d = snap.to_dict()
        assert set(d.keys()) == {"action", "center_x", "fingers", "has_hand"}
        assert d["action"] == "JUMP"


# ---------------------------------------------------------------------------
# TelemetrySnapshot
# ---------------------------------------------------------------------------

class TestTelemetrySnapshot:
    def test_timestamp_is_iso_utc(self) -> None:
        snap = TelemetrySnapshot(
            action=Action.LEFT, fps=30, has_hand=True, profile="default", center_x=0.2
        )
        # ISO 8601 with UTC offset or Z suffix
        assert "T" in snap.timestamp

    def test_round_trip_serialisation(self) -> None:
        original = TelemetrySnapshot(
            action=Action.RIGHT, fps=45, has_hand=False, profile="pro", center_x=0.75
        )
        restored = TelemetrySnapshot.from_dict(original.to_dict())
        assert restored.action == original.action
        assert restored.fps == original.fps
        assert restored.profile == original.profile

    def test_center_x_is_rounded_in_dict(self) -> None:
        snap = TelemetrySnapshot(
            action=Action.CENTER, fps=30, has_hand=True, profile="default", center_x=0.123456789
        )
        assert len(str(snap.to_dict()["center_x"]).split(".")[-1]) <= 4
