from __future__ import annotations

import time

from pynput.keyboard import Controller, Key

from src.domain.actions import Action


class KeyboardAdapter:
    def __init__(self, key_map: dict[str, str], cooldown_ms: int):
        self._keyboard = Controller()
        self._key_map = key_map
        self._cooldown_ms = cooldown_ms
        self._last_sent: dict[Action, float] = {}

    def send(self, action: Action) -> bool:
        if action not in {Action.JUMP, Action.SLIDE, Action.LEFT, Action.RIGHT, Action.HOVERBOARD}:
            return False
        if not self._within_cooldown(action):
            return False

        key_token = self._key_map.get(action.value, "").strip().lower()
        key_obj = self._token_to_key(key_token)
        if key_obj is None:
            return False

        self._keyboard.press(key_obj)
        self._keyboard.release(key_obj)
        self._last_sent[action] = time.perf_counter()
        return True

    def _within_cooldown(self, action: Action) -> bool:
        last_sent = self._last_sent.get(action)
        if last_sent is None:
            return True
        elapsed_ms = (time.perf_counter() - last_sent) * 1000
        return elapsed_ms >= self._cooldown_ms

    @staticmethod
    def _token_to_key(token: str):
        if token == "up":
            return Key.up
        if token == "down":
            return Key.down
        if token == "left":
            return Key.left
        if token == "right":
            return Key.right
        if token == "space":
            return Key.space
        if len(token) == 1 and token.isprintable():
            return token
        return None

