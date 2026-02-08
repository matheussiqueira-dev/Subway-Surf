from dataclasses import dataclass

from src.domain.actions import Action
from src.services.gesture_service import GestureInterpreter


@dataclass
class Landmark:
    x: float
    y: float


def build_hand(fingers: list[bool], center_x: float = 0.5):
    hand = [Landmark(center_x, 0.8) for _ in range(21)]

    hand[0] = Landmark(center_x, 0.8)  # wrist
    hand[2] = Landmark(center_x - 0.02, 0.55)  # thumb mcp
    hand[4] = Landmark(center_x - 0.02, 0.42 if fingers[0] else 0.75)  # thumb tip

    # index
    hand[6] = Landmark(center_x - 0.01, 0.58)
    hand[8] = Landmark(center_x - 0.01, 0.38 if fingers[1] else 0.74)
    # middle
    hand[10] = Landmark(center_x, 0.58)
    hand[12] = Landmark(center_x, 0.38 if fingers[2] else 0.74)
    # ring
    hand[14] = Landmark(center_x + 0.01, 0.58)
    hand[16] = Landmark(center_x + 0.01, 0.38 if fingers[3] else 0.74)
    # pinky
    hand[18] = Landmark(center_x + 0.02, 0.58)
    hand[20] = Landmark(center_x + 0.02, 0.38 if fingers[4] else 0.74)
    return [hand]


def test_interpret_jump():
    interpreter = GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.0)
    snapshot = interpreter.interpret(build_hand([True, True, True, True, True]))
    assert snapshot.action == Action.JUMP


def test_interpret_slide():
    interpreter = GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.0)
    snapshot = interpreter.interpret(build_hand([True, False, False, False, True]))
    assert snapshot.action == Action.SLIDE


def test_interpret_hoverboard():
    interpreter = GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.0)
    snapshot = interpreter.interpret(build_hand([False, True, True, False, False]))
    assert snapshot.action == Action.HOVERBOARD


def test_interpret_lane_left():
    interpreter = GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.0)
    snapshot = interpreter.interpret(build_hand([False, False, False, False, False], center_x=0.2))
    assert snapshot.action == Action.LEFT


def test_interpret_lane_right():
    interpreter = GestureInterpreter(left_bound=0.35, right_bound=0.65, smoothing=0.0)
    snapshot = interpreter.interpret(build_hand([False, False, False, False, False], center_x=0.8))
    assert snapshot.action == Action.RIGHT

