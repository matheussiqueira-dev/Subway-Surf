from __future__ import annotations

from typing import Any, Sequence

from src.domain.actions import Action
from src.domain.models import GestureSnapshot

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
    def __init__(self, left_bound: float, right_bound: float, smoothing: float = 0.22):
        if not 0.05 <= left_bound < right_bound <= 0.95:
            raise ValueError("Invalid lane configuration.")
        if not 0.0 <= smoothing <= 1.0:
            raise ValueError("Smoothing must be between 0.0 and 1.0.")
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.smoothing = smoothing
        self._smoothed_center: float | None = None

    def update_bounds(self, left_bound: float, right_bound: float) -> None:
        if not 0.05 <= left_bound < right_bound <= 0.95:
            raise ValueError("Invalid lane configuration.")
        self.left_bound = left_bound
        self.right_bound = right_bound

    def interpret(self, hand_landmarks: Sequence[Sequence[Any]] | None) -> GestureSnapshot:
        if not hand_landmarks:
            self._smoothed_center = None
            return GestureSnapshot(action=Action.IDLE, has_hand=False)

        hand = hand_landmarks[0]
        fingers = self._check_fingers(hand)
        center_x = self._calculate_center_x(hand)
        center_x = self._smooth_center(center_x)
        action = self._resolve_action(fingers, center_x)

        return GestureSnapshot(
            action=action,
            center_x=center_x,
            fingers=fingers,
            has_hand=True,
        )

    def _smooth_center(self, center_x: float) -> float:
        if self._smoothed_center is None:
            self._smoothed_center = center_x
            return center_x
        self._smoothed_center = (1 - self.smoothing) * self._smoothed_center + (
            self.smoothing * center_x
        )
        return self._smoothed_center

    @staticmethod
    def _calculate_center_x(hand: Sequence[Any]) -> float:
        # Weighted center with wrist and first two fingertips for stable lane mapping.
        return (hand[0].x * 0.4) + (hand[INDEX_TIP].x * 0.3) + (hand[THUMB_TIP].x * 0.3)

    @staticmethod
    def _check_fingers(hand: Sequence[Any]) -> list[bool]:
        fingers = [False] * 5

        fingers[0] = hand[THUMB_TIP].y < hand[THUMB_MCP].y
        fingers[1] = hand[INDEX_TIP].y < hand[INDEX_PIP].y
        fingers[2] = hand[MIDDLE_TIP].y < hand[MIDDLE_PIP].y
        fingers[3] = hand[RING_TIP].y < hand[RING_PIP].y
        fingers[4] = hand[PINKY_TIP].y < hand[PINKY_PIP].y
        return fingers

    def _resolve_action(self, fingers: list[bool], center_x: float) -> Action:
        if all(fingers):
            return Action.JUMP

        if fingers[0] and fingers[4] and not any(fingers[1:4]):
            return Action.SLIDE

        if fingers[1] and fingers[2] and not fingers[0] and not any(fingers[3:]):
            return Action.HOVERBOARD

        if center_x < self.left_bound:
            return Action.LEFT
        if center_x > self.right_bound:
            return Action.RIGHT
        return Action.CENTER

