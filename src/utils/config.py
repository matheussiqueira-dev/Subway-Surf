from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env_int(name: str, default: int, min_value: int | None = None) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    if min_value is not None and value < min_value:
        return default
    return value


def _env_float(
    name: str, default: float, min_value: float | None = None, max_value: float | None = None
) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    if min_value is not None and value < min_value:
        return default
    if max_value is not None and value > max_value:
        return default
    return value


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class AppConfig:
    project_root: Path
    model_path: Path
    camera_name: str
    camera_index: int
    frame_width: int
    frame_height: int
    left_bound: float
    right_bound: float
    detection_confidence: float
    presence_confidence: float
    tracking_confidence: float
    cooldown_ms: int
    window_title: str
    game_window_title: str
    auto_focus_window: bool
    key_map: dict[str, str]
    log_level: str
    logs_dir: Path
    profiles_dir: Path
    runtime_dir: Path
    telemetry_file: Path
    active_profile_file: Path
    api_host: str
    api_port: int
    api_key: str
    api_allow_origins: tuple[str, ...] = field(default_factory=lambda: ("*",))

    def ensure_directories(self) -> None:
        for path in (self.logs_dir, self.profiles_dir, self.runtime_dir):
            path.mkdir(parents=True, exist_ok=True)

    def to_public_dict(self) -> dict[str, object]:
        return {
            "camera_name": self.camera_name,
            "camera_index": self.camera_index,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "left_bound": self.left_bound,
            "right_bound": self.right_bound,
            "detection_confidence": self.detection_confidence,
            "presence_confidence": self.presence_confidence,
            "tracking_confidence": self.tracking_confidence,
            "cooldown_ms": self.cooldown_ms,
            "window_title": self.window_title,
            "game_window_title": self.game_window_title,
            "auto_focus_window": self.auto_focus_window,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "api_key_enabled": bool(self.api_key),
        }


def load_config(project_root: Path | None = None) -> AppConfig:
    root = project_root or Path(__file__).resolve().parents[2]
    runtime_dir = root / "runtime"
    config = AppConfig(
        project_root=root,
        model_path=root / "hand_landmarker.task",
        camera_name=os.environ.get("CAMERA_NAME", "BRIO"),
        camera_index=_env_int("CAMERA_INDEX", 0, min_value=0),
        frame_width=_env_int("FRAME_WIDTH", 640, min_value=320),
        frame_height=_env_int("FRAME_HEIGHT", 480, min_value=240),
        left_bound=_env_float("LEFT_BOUND", 0.35, min_value=0.05, max_value=0.9),
        right_bound=_env_float("RIGHT_BOUND", 0.65, min_value=0.1, max_value=0.95),
        detection_confidence=_env_float(
            "DETECTION_CONFIDENCE", 0.7, min_value=0.1, max_value=1.0
        ),
        presence_confidence=_env_float("PRESENCE_CONFIDENCE", 0.7, min_value=0.1, max_value=1.0),
        tracking_confidence=_env_float("TRACKING_CONFIDENCE", 0.6, min_value=0.1, max_value=1.0),
        cooldown_ms=_env_int("ACTION_COOLDOWN_MS", 220, min_value=80),
        window_title=os.environ.get("WINDOW_TITLE", "Subway Surfers Motion Controller"),
        game_window_title=os.environ.get("GAME_WINDOW_TITLE", "Subway Surfers"),
        auto_focus_window=_env_bool("AUTO_FOCUS_WINDOW", True),
        key_map={
            "JUMP": "up",
            "SLIDE": "down",
            "LEFT": "left",
            "RIGHT": "right",
            "HOVERBOARD": "space",
        },
        log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        logs_dir=runtime_dir / "logs",
        profiles_dir=root / "profiles",
        runtime_dir=runtime_dir,
        telemetry_file=runtime_dir / "telemetry.json",
        active_profile_file=runtime_dir / "active_profile.txt",
        api_host=os.environ.get("API_HOST", "127.0.0.1"),
        api_port=_env_int("API_PORT", 8000, min_value=1),
        api_key=os.environ.get("API_KEY", "").strip(),
        api_allow_origins=tuple(
            origin.strip()
            for origin in os.environ.get("API_ALLOW_ORIGINS", "*").split(",")
            if origin.strip()
        )
        or ("*",),
    )
    if config.left_bound >= config.right_bound:
        config.left_bound, config.right_bound = 0.35, 0.65
    config.ensure_directories()
    return config

