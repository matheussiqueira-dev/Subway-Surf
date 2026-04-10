"""Shared pytest fixtures for the Subway Surf test suite."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.domain.actions import Action
from src.domain.models import Profile
from src.services.profile_service import ProfileService
from src.services.telemetry_service import TelemetryService
from src.utils.config import load_config


# ---------------------------------------------------------------------------
# Lightweight hand-landmark stub
# ---------------------------------------------------------------------------

@dataclass
class Landmark:
    """Minimal stub that mirrors mediapipe NormalizedLandmark."""

    x: float
    y: float
    z: float = 0.0


def make_hand(fingers: list[bool], center_x: float = 0.5) -> list[list[Landmark]]:
    """Build a single-hand landmark list for the 21 MediaPipe keypoints.

    *fingers*: 5-element list of bool — [thumb, index, middle, ring, pinky].
    *center_x*: normalised X position of the wrist.
    """
    hand: list[Landmark] = [Landmark(center_x, 0.8) for _ in range(21)]

    # Wrist
    hand[0] = Landmark(center_x, 0.8)

    # Thumb: MCP at y=0.55, tip above (y<MCP) when extended
    hand[2] = Landmark(center_x - 0.02, 0.55)
    hand[4] = Landmark(center_x - 0.02, 0.42 if fingers[0] else 0.75)

    # Index
    hand[6] = Landmark(center_x - 0.01, 0.58)
    hand[8] = Landmark(center_x - 0.01, 0.38 if fingers[1] else 0.74)

    # Middle
    hand[10] = Landmark(center_x, 0.58)
    hand[12] = Landmark(center_x, 0.38 if fingers[2] else 0.74)

    # Ring
    hand[14] = Landmark(center_x + 0.01, 0.58)
    hand[16] = Landmark(center_x + 0.01, 0.38 if fingers[3] else 0.74)

    # Pinky
    hand[18] = Landmark(center_x + 0.02, 0.58)
    hand[20] = Landmark(center_x + 0.02, 0.38 if fingers[4] else 0.74)

    return [hand]


# ---------------------------------------------------------------------------
# Service fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def profile_service(tmp_path: Path) -> ProfileService:
    return ProfileService(
        profiles_dir=tmp_path / "profiles",
        active_profile_file=tmp_path / "runtime" / "active_profile.txt",
    )


@pytest.fixture()
def telemetry_service(tmp_path: Path) -> TelemetryService:
    return TelemetryService(telemetry_file=tmp_path / "telemetry.json")


@pytest.fixture()
def default_profile() -> Profile:
    return Profile(name="default")


@pytest.fixture()
def app_config(tmp_path: Path):
    return load_config(project_root=tmp_path)


# ---------------------------------------------------------------------------
# Mock keyboard for GameController tests (no real key-presses)
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_keyboard():
    kb = MagicMock()
    kb.send.return_value = True
    return kb
