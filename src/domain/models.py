from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .actions import Action, parse_action

PROFILE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,40}$")


@dataclass(slots=True)
class Profile:
    name: str
    description: str = "Default profile"
    left_bound: float = 0.35
    right_bound: float = 0.65
    detection_confidence: float = 0.7
    presence_confidence: float = 0.7
    tracking_confidence: float = 0.6
    cooldown_ms: int = 220

    def validate(self) -> None:
        if not PROFILE_NAME_PATTERN.match(self.name):
            raise ValueError(
                "Profile name must contain only letters, numbers, '_' or '-'."
            )
        if not 0.05 <= self.left_bound < self.right_bound <= 0.95:
            raise ValueError("Lane boundaries must satisfy 0.05 <= left < right <= 0.95.")
        for label, value in (
            ("detection_confidence", self.detection_confidence),
            ("presence_confidence", self.presence_confidence),
            ("tracking_confidence", self.tracking_confidence),
        ):
            if not 0.1 <= value <= 1.0:
                raise ValueError(f"{label} must be between 0.1 and 1.0.")
        if not 80 <= self.cooldown_ms <= 1200:
            raise ValueError("cooldown_ms must be between 80 and 1200.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "left_bound": self.left_bound,
            "right_bound": self.right_bound,
            "detection_confidence": self.detection_confidence,
            "presence_confidence": self.presence_confidence,
            "tracking_confidence": self.tracking_confidence,
            "cooldown_ms": self.cooldown_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Profile":
        profile = cls(
            name=str(data["name"]),
            description=str(data.get("description", "Default profile")),
            left_bound=float(data.get("left_bound", 0.35)),
            right_bound=float(data.get("right_bound", 0.65)),
            detection_confidence=float(data.get("detection_confidence", 0.7)),
            presence_confidence=float(data.get("presence_confidence", 0.7)),
            tracking_confidence=float(data.get("tracking_confidence", 0.6)),
            cooldown_ms=int(data.get("cooldown_ms", 220)),
        )
        profile.validate()
        return profile


@dataclass(slots=True)
class GestureSnapshot:
    action: Action = Action.IDLE
    center_x: float = 0.5
    fingers: list[bool] = field(default_factory=lambda: [False] * 5)
    has_hand: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "center_x": self.center_x,
            "fingers": self.fingers,
            "has_hand": self.has_hand,
        }


@dataclass(slots=True)
class TelemetrySnapshot:
    action: Action
    fps: int
    has_hand: bool
    profile: str
    center_x: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "fps": self.fps,
            "has_hand": self.has_hand,
            "profile": self.profile,
            "center_x": round(self.center_x, 4),
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TelemetrySnapshot":
        return cls(
            action=parse_action(str(data.get("action", "IDLE"))),
            fps=int(data.get("fps", 0)),
            has_hand=bool(data.get("has_hand", False)),
            profile=str(data.get("profile", "default")),
            center_x=float(data.get("center_x", 0.5)),
            timestamp=str(data.get("timestamp", "")) or datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
        )

