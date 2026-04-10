"""Unit tests for AppConfig and load_config()."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.config import AppConfig, load_config


def test_load_config_returns_app_config(tmp_path: Path) -> None:
    cfg = load_config(project_root=tmp_path)
    assert isinstance(cfg, AppConfig)


def test_directories_are_created(tmp_path: Path) -> None:
    cfg = load_config(project_root=tmp_path)
    assert cfg.logs_dir.exists()
    assert cfg.profiles_dir.exists()
    assert cfg.runtime_dir.exists()


def test_default_values_are_sensible(tmp_path: Path) -> None:
    cfg = load_config(project_root=tmp_path)
    assert cfg.camera_index == 0
    assert cfg.frame_width == 640
    assert cfg.frame_height == 480
    assert 0.05 <= cfg.left_bound < cfg.right_bound <= 0.95
    assert cfg.api_port == 8000


def test_env_override_camera_index(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"CAMERA_INDEX": "2"}):
        cfg = load_config(project_root=tmp_path)
    assert cfg.camera_index == 2


def test_env_override_log_level(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"LOG_LEVEL": "debug"}):
        cfg = load_config(project_root=tmp_path)
    assert cfg.log_level == "DEBUG"


def test_inverted_bounds_reset_to_defaults(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"LEFT_BOUND": "0.80", "RIGHT_BOUND": "0.20"}):
        cfg = load_config(project_root=tmp_path)
    assert cfg.left_bound == 0.35
    assert cfg.right_bound == 0.65


def test_to_public_dict_excludes_api_key(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"API_KEY": "super-secret"}):
        cfg = load_config(project_root=tmp_path)
    public = cfg.to_public_dict()
    assert "api_key" not in public
    assert public["api_key_enabled"] is True


def test_to_public_dict_api_key_enabled_false_when_empty(tmp_path: Path) -> None:
    with patch.dict(os.environ, {"API_KEY": ""}):
        cfg = load_config(project_root=tmp_path)
    assert cfg.to_public_dict()["api_key_enabled"] is False


def test_env_bool_parses_truthy_values(tmp_path: Path) -> None:
    for value in ("1", "true", "yes", "on", "True", "YES"):
        with patch.dict(os.environ, {"AUTO_FOCUS_WINDOW": value}):
            cfg = load_config(project_root=tmp_path)
        assert cfg.auto_focus_window is True, f"Expected True for '{value}'"


def test_env_bool_parses_falsy_values(tmp_path: Path) -> None:
    for value in ("0", "false", "no", "off"):
        with patch.dict(os.environ, {"AUTO_FOCUS_WINDOW": value}):
            cfg = load_config(project_root=tmp_path)
        assert cfg.auto_focus_window is False, f"Expected False for '{value}'"
