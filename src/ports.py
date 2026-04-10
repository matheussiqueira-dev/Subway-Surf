"""
Structural interfaces (Protocols) for the application's core dependencies.

These Protocols define the contracts that infrastructure adapters must satisfy.
Using Protocol instead of ABC keeps dependencies optional: any object that
implements the right methods is accepted without explicit inheritance, which
makes mocking in tests trivial.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import numpy as np

from src.domain.actions import Action
from src.domain.models import GestureSnapshot


@runtime_checkable
class CameraPort(Protocol):
    """Wraps a video capture device."""

    def open(self) -> bool:
        """Open the device. Returns True on success."""
        ...

    def is_opened(self) -> bool:
        """Return True while the device is ready to deliver frames."""
        ...

    def read(self) -> tuple[bool, np.ndarray | None]:
        """Read the next frame. Returns (success, frame_or_None)."""
        ...

    def release(self) -> None:
        """Release the device and free resources."""
        ...


@runtime_checkable
class DetectorPort(Protocol):
    """Runs hand-landmark detection on a single RGB frame."""

    def detect(self, rgb_image: np.ndarray) -> Any:
        """Return a detection result object (framework-specific)."""
        ...

    def close(self) -> None:
        """Release the model resources."""
        ...


@runtime_checkable
class KeyboardPort(Protocol):
    """Translates an Action into a physical key-press."""

    def send(self, action: Action) -> bool:
        """Press the key mapped to *action*.

        Returns True if the key was sent, False if rejected
        (unknown action, cooldown not elapsed, no mapping found).
        """
        ...


@runtime_checkable
class GestureInterpreterPort(Protocol):
    """Converts raw hand-landmark data into a GestureSnapshot."""

    def interpret(self, hand_landmarks: Any) -> GestureSnapshot:
        """Return the gesture inferred from *hand_landmarks*."""
        ...

    def update_bounds(self, left_bound: float, right_bound: float) -> None:
        """Hot-reload lane boundaries without recreating the object."""
        ...
