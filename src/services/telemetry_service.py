from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from src.domain.models import TelemetrySnapshot


class TelemetryService:
    def __init__(self, telemetry_file: Path, max_history: int = 500):
        self.telemetry_file = telemetry_file
        self.max_history = max_history
        self._lock = Lock()
        self._latest: TelemetrySnapshot | None = None
        self.telemetry_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.telemetry_file.exists():
            self.telemetry_file.write_text("[]", encoding="utf-8")

    def publish(self, snapshot: TelemetrySnapshot) -> None:
        with self._lock:
            self._latest = snapshot
            history = self._load_history()
            history.append(snapshot.to_dict())
            if len(history) > self.max_history:
                history = history[-self.max_history :]
            self.telemetry_file.write_text(
                json.dumps(history, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def latest(self) -> TelemetrySnapshot | None:
        with self._lock:
            return self._latest

    def history(self, limit: int = 60) -> list[dict[str, object]]:
        limit = max(1, min(limit, self.max_history))
        with self._lock:
            history = self._load_history()
            return history[-limit:]

    def _load_history(self) -> list[dict[str, object]]:
        try:
            return json.loads(self.telemetry_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

