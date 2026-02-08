import pytest

from src.domain.models import Profile
from src.services.profile_service import ProfileService


def test_profile_service_bootstraps_default(tmp_path):
    service = ProfileService(
        profiles_dir=tmp_path / "profiles",
        active_profile_file=tmp_path / "runtime" / "active_profile.txt",
    )
    active = service.get_active_profile()
    assert active.name == "default"
    assert (tmp_path / "profiles" / "default.json").exists()


def test_profile_save_and_activate(tmp_path):
    service = ProfileService(
        profiles_dir=tmp_path / "profiles",
        active_profile_file=tmp_path / "runtime" / "active_profile.txt",
    )
    profile = Profile(
        name="pro_competitive",
        description="Low latency mode",
        left_bound=0.32,
        right_bound=0.68,
        detection_confidence=0.75,
        presence_confidence=0.75,
        tracking_confidence=0.65,
        cooldown_ms=180,
    )
    service.save_profile(profile)
    activated = service.activate_profile("pro_competitive")

    assert activated.name == "pro_competitive"
    assert service.get_active_profile_name() == "pro_competitive"


def test_profile_invalid_name_rejected(tmp_path):
    service = ProfileService(
        profiles_dir=tmp_path / "profiles",
        active_profile_file=tmp_path / "runtime" / "active_profile.txt",
    )
    with pytest.raises(ValueError):
        service.get_profile("../unsafe")

