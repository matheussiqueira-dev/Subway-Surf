"""Unit tests for ProfileService."""

from __future__ import annotations

import pytest

from src.domain.models import Profile
from src.services.profile_service import ProfileService

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def test_bootstraps_default_profile(profile_service: ProfileService) -> None:
    active = profile_service.get_active_profile()
    assert active.name == "default"


def test_default_profile_file_created(profile_service: ProfileService) -> None:
    profile_service.get_active_profile()
    assert (profile_service.profiles_dir / "default.json").exists()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def test_save_and_retrieve_profile(profile_service: ProfileService) -> None:
    profile = Profile(
        name="pro_competitive",
        description="Low latency mode",
        left_bound=0.32,
        right_bound=0.68,
        cooldown_ms=180,
    )
    profile_service.save_profile(profile)
    loaded = profile_service.get_profile("pro_competitive")
    assert loaded.name == "pro_competitive"
    assert loaded.cooldown_ms == 180


def test_list_profiles_includes_saved(profile_service: ProfileService) -> None:
    profile_service.save_profile(Profile(name="night_mode"))
    names = [p.name for p in profile_service.list_profiles()]
    assert "default" in names
    assert "night_mode" in names


def test_activate_profile_updates_active(profile_service: ProfileService) -> None:
    profile_service.save_profile(Profile(name="second"))
    profile_service.activate_profile("second")
    assert profile_service.get_active_profile_name() == "second"


def test_get_active_profile_follows_activation(profile_service: ProfileService) -> None:
    profile_service.save_profile(Profile(name="turbo", cooldown_ms=100))
    profile_service.activate_profile("turbo")
    active = profile_service.get_active_profile()
    assert active.name == "turbo"
    assert active.cooldown_ms == 100


# ---------------------------------------------------------------------------
# Validation & error cases
# ---------------------------------------------------------------------------


def test_invalid_profile_name_raises(profile_service: ProfileService) -> None:
    with pytest.raises(ValueError):
        profile_service.get_profile("../unsafe")


def test_missing_profile_raises_file_not_found(profile_service: ProfileService) -> None:
    with pytest.raises(FileNotFoundError):
        profile_service.get_profile("nonexistent")


def test_invalid_profile_data_raises_on_save(profile_service: ProfileService) -> None:
    bad = Profile(name="bad", left_bound=0.80, right_bound=0.20)
    with pytest.raises(ValueError):
        profile_service.save_profile(bad)


# ---------------------------------------------------------------------------
# Resilience
# ---------------------------------------------------------------------------


def test_list_profiles_skips_corrupt_files(profile_service: ProfileService) -> None:
    corrupt = profile_service.profiles_dir / "corrupt.json"
    corrupt.write_text("NOT JSON", encoding="utf-8")
    # Should not raise; corrupt entry is silently skipped.
    profiles = profile_service.list_profiles()
    assert all(p.name != "corrupt" for p in profiles)


def test_get_active_falls_back_to_default_when_file_missing(
    profile_service: ProfileService,
) -> None:
    profile_service.active_profile_file.unlink(missing_ok=True)
    active = profile_service.get_active_profile()
    assert active.name == "default"
