from __future__ import annotations

from typing import Any, Sequence

from src.domain.actions import Action
from src.domain.models import GestureSnapshot

# MediaPipe hand landmark indices used for gesture recognition.
# Reference: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
THUMB_TIP = 4
THUMB_MCP = 2
INDEX_TIP = 8
INDEX_PIP = 6
MIDDLE_TIP = 12
MIDDLE_PIP = 10
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18


class GestureInterpreter:
    """Maps MediaPipe hand landmarks to game Actions.

    Finger detection
    ----------------
    Each finger is considered *extended* when its tip y-coordinate is above
    (numerically lower than) its proximal interphalangeal (PIP) joint.
    The thumb is compared against its MCP joint instead.

    Action priority (highest → lowest):
    1. JUMP         — all five fingers extended
    2. SLIDE        — thumb + pinky only
    3. HOVERBOARD   — index + middle only
    4. LEFT / RIGHT — hand position relative to lane bounds
    5. CENTER       — hand inside bounds

    Smoothing
    ---------
    An exponential moving average (EMA) with configurable *smoothing* alpha
    stabilises the X-centre used for lane detection.  ``smoothing=0.0``
    disables smoothing (raw value each frame); ``smoothing=1.0`` freezes the
    value at the first observed position.
    """

    def __init__(
        self,
        left_bound: float,
        right_bound: float,
        smoothing: float = 0.22,
    ) -> None:
        if not 0.05 <= left_bound < right_bound <= 0.95:
            raise ValueError(
                f"Invalid lane configuration: left_bound={left_bound}, right_bound={right_bound}. "
                "Must satisfy 0.05 <= left_bound < right_bound <= 0.95."
            )
        if not 0.0 <= smoothing <= 1.0:
            raise ValueError(f"smoothing must be in [0.0, 1.0], got {smoothing}.")
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.smoothing = smoothing
        self._smoothed_center: float | None = None

    def update_bounds(self, left_bound: float, right_bound: float) -> None:
        """Hot-reload lane boundaries without recreating the interpreter."""
        if not 0.05 <= left_bound < right_bound <= 0.95:
            raise ValueError(
                f"Invalid lane configuration: left_bound={left_bound}, right_bound={right_bound}."
            )
        self.left_bound = left_bound
        self.right_bound = right_bound

    def interpret(self, hand_landmarks: Sequence[Sequence[Any]] | None) -> GestureSnapshot:
        """Convert raw landmark data to a GestureSnapshot.

        Args:
            hand_landmarks: Outer list = detected hands; inner list = 21 landmarks.
                            Pass ``None`` or an empty sequence when no hand is present.

        Returns:
            A GestureSnapshot with the resolved action and smoothed center X.
        """
        if not hand_landmarks:
            self._smoothed_center = None
            return GestureSnapshot(action=Action.IDLE, has_hand=False)

        hand = hand_landmarks[0]
        fingers = self._detect_fingers(hand)
        raw_center = self._weighted_center_x(hand)
        smoothed = self._apply_ema(raw_center)
        action = self._resolve_action(fingers, smoothed)

        return GestureSnapshot(
            action=action,
            center_x=smoothed,
            fingers=fingers,
            has_hand=True,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _apply_ema(self, value: float) -> float:
        """Apply exponential moving average to stabilise the X position."""
        if self._smoothed_center is None:
            self._smoothed_center = value
            return value
        self._smoothed_center = (
            (1.0 - self.smoothing) * self._smoothed_center + self.smoothing * value
        )
        return self._smoothed_center

    @staticmethod
    def _weighted_center_x(hand: Sequence[Any]) -> float:
        """Compute a weighted X-centre from wrist and two fingertips.

        Weighting wrist (0.4) + index-tip (0.3) + thumb-tip (0.3) produces
        a stable estimate that is more robust to single-landmark noise than
        using the wrist alone.
        """
        return hand[0].x * 0.4 + hand[INDEX_TIP].x * 0.3 + hand[THUMB_TIP].x * 0.3

    @staticmethod
    def _detect_fingers(hand: Sequence[Any]) -> list[bool]:
        """Return a 5-element list [thumb, index, middle, ring, pinky].

        A finger is *extended* when tip.y < pip.y (Y increases downward in
        normalised coordinates, so a lower Y means higher on screen).
        """
        return [
            hand[THUMB_TIP].y < hand[THUMB_MCP].y,
            hand[INDEX_TIP].y < hand[INDEX_PIP].y,
            hand[MIDDLE_TIP].y < hand[MIDDLE_PIP].y,
            hand[RING_TIP].y < hand[RING_PIP].y,
            hand[PINKY_TIP].y < hand[PINKY_PIP].y,
        ]

    def _resolve_action(self, fingers: list[bool], center_x: float) -> Action:
        thumb, index, middle, ring, pinky = fingers

        if all(fingers):
            return Action.JUMP

        if thumb and pinky and not index and not middle and not ring:
            return Action.SLIDE

        if index and middle and not thumb and not ring and not pinky:
            return Action.HOVERBOARD

        if center_x < self.left_bound:
            return Action.LEFT
        if center_x > self.right_bound:
            return Action.RIGHT
        return Action.CENTER
