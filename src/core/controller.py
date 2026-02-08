from __future__ import annotations

import logging

from src.domain.actions import Action, DISCRETE_ACTIONS
from src.infrastructure.keyboard_adapter import KeyboardAdapter

try:
    import pygetwindow as gw
except ImportError:  # pragma: no cover - optional runtime dependency
    gw = None


class GameController:
    def __init__(
        self,
        keyboard: KeyboardAdapter,
        window_title: str,
        auto_focus_window: bool = True,
    ):
        self.keyboard = keyboard
        self.window_title = window_title
        self.auto_focus_window = auto_focus_window
        self._last_lane_action = Action.CENTER
        self._discrete_state = {action: False for action in DISCRETE_ACTIONS}
        self._logger = logging.getLogger(self.__class__.__name__)
        self._focus_attempted = False

    def perform_action(self, action: Action) -> None:
        if action == Action.IDLE:
            self._reset_discrete()
            return

        self._focus_window_once()

        if action in DISCRETE_ACTIONS:
            if not self._discrete_state[action] and self.keyboard.send(action):
                self._discrete_state[action] = True
            return

        self._reset_discrete()
        if action == Action.CENTER:
            self._last_lane_action = Action.CENTER
            return

        if action != self._last_lane_action and self.keyboard.send(action):
            self._last_lane_action = action

    def _reset_discrete(self) -> None:
        for action in self._discrete_state:
            self._discrete_state[action] = False

    def _focus_window_once(self) -> None:
        if not self.auto_focus_window or self._focus_attempted or gw is None:
            return
        self._focus_attempted = True
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows and not windows[0].isActive:
                windows[0].activate()
                self._logger.info("Focused game window '%s'.", self.window_title)
        except Exception as exc:  # pragma: no cover - OS specific behavior
            self._logger.warning("Could not focus game window: %s", exc)

