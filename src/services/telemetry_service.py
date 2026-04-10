from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from src.domain.models import TelemetrySnapshot


class TelemetryService:
    """Thread-safe telemetry storage with in-memory buffer and JSON persistence.

    Design notes
    ------------
    The service keeps the full history in a ``deque``-style in-memory list so
    that ``publish()`` never needs to read the file back — only append and trim.
    This removes the O(n) read on every publish call that the original
    implementation had, making high-frequency telemetry inexpensive.

    The file is still written on every publish so the REST API always serves
    up-to-date data even when queried by an out-of-process dashboard.
    """

    def __init__(self, telemetry_file: Path, max_history: int = 500) -> None:
        self.telemetry_file = telemetry_file
        self.max_history = max_history
        self._lock = Lock()
        self._latest: TelemetrySnapshot | None = None
        self._history: list[dict[str, Any]] = []

        self.telemetry_file.parent.mkdir(parents=True, exist_ok=True)
        self._history = self._load_from_disk()
        if not self.telemetry_file.exists():
            self._flush()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def publish(self, snapshot: TelemetrySnapshot) -> None:
        """Append *snapshot* to the history buffer and persist to disk."""
        with self._lock:
            self._latest = snapshot
            self._history.append(snapshot.to_dict())
            if len(self._history) > self.max_history:
                self._history = self._history[-self.max_history :]
            self._flush()

    def latest(self) -> TelemetrySnapshot | None:
        """Return the most recently published snapshot, or None."""
        with self._lock:
            return self._latest

    def history(self, limit: int = 60) -> list[dict[str, Any]]:
        """Return the last *limit* snapshots (capped by max_history)."""
        limit = max(1, min(limit, self.max_history))
        with self._lock:
            return list(self._history[-limit:])

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _flush(self) -> None:
        """Write current buffer to disk (must be called under _lock)."""
        self.telemetry_file.write_text(
            json.dumps(self._history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load_from_disk(self) -> list[dict[str, Any]]:
        """Read history from the JSON file, returning [] on any error."""
        try:
            data = json.loads(self.telemetry_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data[-self.max_history :]
            return []
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            return []
