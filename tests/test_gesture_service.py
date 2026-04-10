"""Unit tests for GestureInterpreter."""

from __future__ import annotations

import pytest

from src.domain.actions import Action
from src.services.gesture_service import GestureInterpreter
from tests.conftest import make_hand


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def interpreter() -> GestureInterpreter:
    return GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.0)


# ---------------------------------------------------------------------------
# Discrete gesture recognition
# ---------------------------------------------------------------------------

def test_all_fingers_extended_is_jump(interpreter: GestureInterpreter) -> None:
    snapshot = interpreter.interpret(make_hand([True, True, True, True, True]))
    assert snapshot.action == Action.JUMP
    assert snapshot.has_hand is True


def test_thumb_and_pinky_is_slide(interpreter: GestureInterpreter) -> None:
    snapshot = interpreter.interpret(make_hand([True, False, False, False, True]))
    assert snapshot.action == Action.SLIDE


def test_index_and_middle_is_hoverboard(interpreter: GestureInterpreter) -> None:
    snapshot = interpreter.interpret(make_hand([False, True, True, False, False]))
    assert snapshot.action == Action.HOVERBOARD


# ---------------------------------------------------------------------------
# Lane detection
# ---------------------------------------------------------------------------

def test_hand_left_of_left_bound_is_lane_left(interpreter: GestureInterpreter) -> None:
    snapshot = interpreter.interpret(make_hand([False] * 5, center_x=0.20))
    assert snapshot.action == Action.LEFT


def test_hand_right_of_right_bound_is_lane_right(interpreter: GestureInterpreter) -> None:
    snapshot = interpreter.interpret(make_hand([False] * 5, center_x=0.80))
    assert snapshot.action == Action.RIGHT


def test_hand_inside_bounds_is_center(interpreter: GestureInterpreter) -> None:
    snapshot = interpreter.interpret(make_hand([False] * 5, center_x=0.50))
    assert snapshot.action == Action.CENTER


# ---------------------------------------------------------------------------
# No-hand / idle path
# ---------------------------------------------------------------------------

def test_no_hand_returns_idle(interpreter: GestureInterpreter) -> None:
    snapshot = interpreter.interpret(None)
    assert snapshot.action == Action.IDLE
    assert snapshot.has_hand is False


def test_empty_landmark_list_returns_idle(interpreter: GestureInterpreter) -> None:
    snapshot = interpreter.interpret([])
    assert snapshot.action == Action.IDLE


# ---------------------------------------------------------------------------
# Smoothing
# ---------------------------------------------------------------------------

def test_smoothing_zero_passes_raw_value() -> None:
    interp = GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.0)
    snap = interp.interpret(make_hand([False] * 5, center_x=0.20))
    # With smoothing=0 the smoothed value should equal the raw weighted center.
    assert snap.center_x < 0.35  # still maps to LEFT lane


def test_smoothing_resets_on_hand_lost() -> None:
    interp = GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.5)
    interp.interpret(make_hand([False] * 5, center_x=0.80))
    interp.interpret(None)  # hand lost — reset smoothed state
    snap = interp.interpret(make_hand([False] * 5, center_x=0.20))
    # After reset, first frame uses raw value directly (no historical bias).
    assert snap.center_x < 0.35


# ---------------------------------------------------------------------------
# Boundary validation
# ---------------------------------------------------------------------------

def test_invalid_bounds_raises() -> None:
    with pytest.raises(ValueError):
        GestureInterpreter(left_bound=0.70, right_bound=0.30)


def test_update_bounds_reflects_new_zones() -> None:
    interp = GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.0)
    # After tightening bounds, centre position now falls outside the zone.
    interp.update_bounds(left_bound=0.45, right_bound=0.55)
    snap = interp.interpret(make_hand([False] * 5, center_x=0.40))
    assert snap.action == Action.LEFT
