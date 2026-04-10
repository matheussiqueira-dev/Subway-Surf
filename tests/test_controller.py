"""Unit tests for GameController."""

from __future__ import annotations

from unittest.mock import MagicMock, call

import pytest

from src.core.controller import GameController
from src.domain.actions import Action


@pytest.fixture()
def controller(mock_keyboard: MagicMock) -> GameController:
    return GameController(
        keyboard=mock_keyboard,
        window_title="Test Window",
        auto_focus_window=False,
    )


# ---------------------------------------------------------------------------
# IDLE resets discrete state
# ---------------------------------------------------------------------------

def test_idle_resets_discrete_state(controller: GameController, mock_keyboard: MagicMock) -> None:
    # Trigger a jump so the state is marked active.
    controller.perform_action(Action.JUMP)
    assert controller._discrete_state[Action.JUMP] is True

    # IDLE should clear all discrete states.
    controller.perform_action(Action.IDLE)
    assert all(not v for v in controller._discrete_state.values())
    # No key sent for IDLE itself.
    mock_keyboard.send.assert_called_once_with(Action.JUMP)


# ---------------------------------------------------------------------------
# Discrete actions are sent only once until reset
# ---------------------------------------------------------------------------

def test_discrete_action_sent_only_once(controller: GameController, mock_keyboard: MagicMock) -> None:
    controller.perform_action(Action.JUMP)
    controller.perform_action(Action.JUMP)  # second call — already active
    assert mock_keyboard.send.call_count == 1


def test_discrete_action_resent_after_idle(controller: GameController, mock_keyboard: MagicMock) -> None:
    controller.perform_action(Action.JUMP)
    controller.perform_action(Action.IDLE)
    controller.perform_action(Action.JUMP)
    assert mock_keyboard.send.call_count == 2


def test_all_discrete_actions_work(controller: GameController, mock_keyboard: MagicMock) -> None:
    for action in (Action.JUMP, Action.SLIDE, Action.HOVERBOARD):
        controller.perform_action(Action.IDLE)  # reset between each
        controller.perform_action(action)
    assert mock_keyboard.send.call_count == 3


# ---------------------------------------------------------------------------
# Lane (continuous) actions
# ---------------------------------------------------------------------------

def test_center_does_not_send_key(controller: GameController, mock_keyboard: MagicMock) -> None:
    controller.perform_action(Action.CENTER)
    mock_keyboard.send.assert_not_called()


def test_lane_action_sent_on_change(controller: GameController, mock_keyboard: MagicMock) -> None:
    controller.perform_action(Action.LEFT)
    mock_keyboard.send.assert_called_once_with(Action.LEFT)


def test_same_lane_action_not_resent(controller: GameController, mock_keyboard: MagicMock) -> None:
    controller.perform_action(Action.RIGHT)
    controller.perform_action(Action.RIGHT)
    assert mock_keyboard.send.call_count == 1


def test_lane_change_sends_new_key(controller: GameController, mock_keyboard: MagicMock) -> None:
    controller.perform_action(Action.LEFT)
    controller.perform_action(Action.RIGHT)
    assert mock_keyboard.send.call_args_list == [call(Action.LEFT), call(Action.RIGHT)]


def test_center_resets_lane_tracking(controller: GameController, mock_keyboard: MagicMock) -> None:
    controller.perform_action(Action.LEFT)
    controller.perform_action(Action.CENTER)  # resets last lane
    controller.perform_action(Action.LEFT)   # same direction again — should resend
    assert mock_keyboard.send.call_count == 2


# ---------------------------------------------------------------------------
# Keyboard failure (send returns False)
# ---------------------------------------------------------------------------

def test_failed_send_does_not_update_state(mock_keyboard: MagicMock) -> None:
    mock_keyboard.send.return_value = False
    ctrl = GameController(keyboard=mock_keyboard, window_title="T", auto_focus_window=False)
    ctrl.perform_action(Action.JUMP)
    # State should NOT be marked active when the send failed.
    assert ctrl._discrete_state[Action.JUMP] is False
