from __future__ import annotations

import json
from pathlib import Path

from src.domain.models import PROFILE_NAME_PATTERN, Profile


class ProfileService:
    def __init__(self, profiles_dir: Path, active_profile_file: Path):
        self.profiles_dir = profiles_dir
        self.active_profile_file = active_profile_file
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.active_profile_file.parent.mkdir(parents=True, exist_ok=True)
        self._bootstrap()

    def _bootstrap(self) -> None:
        default_profile_path = self._profile_path("default")
        if not default_profile_path.exists():
            default_profile = Profile(
                name="default",
                description="Balanced profile for most players.",
            )
            self.save_profile(default_profile)

        if not self.active_profile_file.exists():
            self.active_profile_file.write_text("default", encoding="utf-8")

    def _profile_path(self, name: str) -> Path:
        return self.profiles_dir / f"{name}.json"

    @staticmethod
    def _validate_name(name: str) -> None:
        if not PROFILE_NAME_PATTERN.match(name):
            raise ValueError("Invalid profile name.")

    def list_profiles(self) -> list[Profile]:
        profiles: list[Profile] = []
        for file in sorted(self.profiles_dir.glob("*.json")):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                profiles.append(Profile.from_dict(data))
            except (json.JSONDecodeError, ValueError, KeyError):
                # Skip corrupted files so API/UI remains available.
                continue
        return profiles

    def get_profile(self, name: str) -> Profile:
        self._validate_name(name)
        path = self._profile_path(name)
        if not path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found.")
        data = json.loads(path.read_text(encoding="utf-8"))
        return Profile.from_dict(data)

    def save_profile(self, profile: Profile) -> Profile:
        profile.validate()
        self._validate_name(profile.name)
        path = self._profile_path(profile.name)
        path.write_text(
            json.dumps(profile.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return profile

    def activate_profile(self, name: str) -> Profile:
        profile = self.get_profile(name)
        self.active_profile_file.write_text(profile.name, encoding="utf-8")
        return profile

    def get_active_profile_name(self) -> str:
        if not self.active_profile_file.exists():
            return "default"
        active = self.active_profile_file.read_text(encoding="utf-8").strip()
        if not active:
            return "default"
        return active

    def get_active_profile(self) -> Profile:
        active = self.get_active_profile_name()
        try:
            return self.get_profile(active)
        except FileNotFoundError:
            return self.activate_profile("default")

