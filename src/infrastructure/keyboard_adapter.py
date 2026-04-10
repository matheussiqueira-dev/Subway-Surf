from __future__ import annotations

import time

from pynput.keyboard import Controller, Key

from src.domain.actions import Action

# Actions that are safe to emit as key-presses.
_SENDABLE_ACTIONS: frozenset[Action] = frozenset(
    {Action.JUMP, Action.SLIDE, Action.LEFT, Action.RIGHT, Action.HOVERBOARD}
)


class KeyboardAdapter:
    """Translates game Actions into physical key-presses via pynput.

    A per-action cooldown prevents key-repeat flooding and mirrors the
    game's built-in input debounce.
    """

    def __init__(self, key_map: dict[str, str], cooldown_ms: int) -> None:
        self._keyboard = Controller()
        self._key_map = key_map
        self._cooldown_ms = cooldown_ms
        self._last_sent: dict[Action, float] = {}

    def send(self, action: Action) -> bool:
        """Press and release the key mapped to *action*.

        Returns True when the key was sent, False when:
        - the action is not in the sendable set
        - the cooldown has not elapsed since the last send for this action
        - no key mapping exists for the action
        """
        if action not in _SENDABLE_ACTIONS:
            return False
        if not self._cooldown_elapsed(action):
            return False

        key_token = self._key_map.get(action.value, "").strip().lower()
        key_obj = self._token_to_key(key_token)
        if key_obj is None:
            return False

        self._keyboard.press(key_obj)
        self._keyboard.release(key_obj)
        self._last_sent[action] = time.perf_counter()
        return True

    def _cooldown_elapsed(self, action: Action) -> bool:
        last = self._last_sent.get(action)
        if last is None:
            return True
        return (time.perf_counter() - last) * 1000 >= self._cooldown_ms

    @staticmethod
    def _token_to_key(token: str) -> Key | str | None:
        """Convert a string token to a pynput Key or single character."""
        _special: dict[str, Key] = {
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "space": Key.space,
        }
        if token in _special:
            return _special[token]
        if len(token) == 1 and token.isprintable():
            return token
        return None
