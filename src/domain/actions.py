from enum import Enum


class Action(str, Enum):
    IDLE = "IDLE"
    CENTER = "CENTER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    JUMP = "JUMP"
    SLIDE = "SLIDE"
    HOVERBOARD = "HOVERBOARD"


DISCRETE_ACTIONS = {Action.JUMP, Action.SLIDE, Action.HOVERBOARD}
LANE_ACTIONS = {Action.LEFT, Action.CENTER, Action.RIGHT}


def parse_action(value: str | Action) -> Action:
    if isinstance(value, Action):
        return value
    try:
        return Action(value.upper())
    except ValueError:
        return Action.IDLE

