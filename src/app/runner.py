from __future__ import annotations

import logging
import time

import cv2

from src.core.controller import GameController
from src.core.detector import HandDetector
from src.domain.actions import Action
from src.domain.models import GestureSnapshot, Profile, TelemetrySnapshot
from src.infrastructure.camera import CameraStream
from src.infrastructure.keyboard_adapter import KeyboardAdapter
from src.services.gesture_service import GestureInterpreter
from src.services.profile_service import ProfileService
from src.services.telemetry_service import TelemetryService
from src.ui.display import HUD
from src.utils.config import AppConfig


class VirtualControllerApp:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.profile_service = ProfileService(config.profiles_dir, config.active_profile_file)
        self.telemetry = TelemetryService(config.telemetry_file)
        self.hud = HUD()
        self.camera = CameraStream(config.camera_index, config.frame_width, config.frame_height)

        self.profile = self.profile_service.get_active_profile()
        self.detector = self._create_detector(self.profile)
        self.gesture = GestureInterpreter(self.profile.left_bound, self.profile.right_bound)
        self.keyboard = KeyboardAdapter(config.key_map, cooldown_ms=self.profile.cooldown_ms)
        self.controller = GameController(
            keyboard=self.keyboard,
            window_title=config.game_window_title,
            auto_focus_window=config.auto_focus_window,
        )

        self._last_frame_time = time.perf_counter()
        self._last_telemetry_push = time.perf_counter()
        self._fps = 0

    def run(self) -> None:
        if not self.camera.open():
            raise RuntimeError("Could not open webcam. Check CAMERA_INDEX and camera permissions.")

        self.logger.info("Controller started with profile '%s'.", self.profile.name)
        self.hud.show_startup_screen(self.config.window_title)

        read_failures = 0
        try:
            while self.camera.is_opened():
                success, frame = self.camera.read()
                if not success:
                    read_failures += 1
                    if read_failures > 30:
                        raise RuntimeError("Camera read failed for too long.")
                    continue
                read_failures = 0

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                detection = self.detector.detect(rgb_frame)

                snapshot = self._resolve_snapshot(detection)
                self.controller.perform_action(snapshot.action)

                self._fps = self._calculate_fps()
                rendered = self.hud.draw(
                    frame=frame,
                    snapshot=snapshot,
                    landmarks=detection.hand_landmarks if detection else None,
                    fps=self._fps,
                    profile_name=self.profile.name,
                )

                cv2.imshow(self.config.window_title, rendered)
                self._maybe_publish_telemetry(snapshot)

                key_code = cv2.waitKey(1) & 0xFF
                if key_code == ord("q"):
                    break
                if key_code == ord("h"):
                    self.hud.toggle_help()
                if key_code == ord("p"):
                    self._cycle_profile()
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        self.logger.info("Shutting down controller.")
        self.camera.release()
        self.detector.close()
        cv2.destroyAllWindows()

    def _resolve_snapshot(self, detection_result) -> GestureSnapshot:
        if detection_result and detection_result.hand_landmarks:
            return self.gesture.interpret(detection_result.hand_landmarks)
        return GestureSnapshot(action=Action.IDLE, has_hand=False)

    def _calculate_fps(self) -> int:
        now = time.perf_counter()
        elapsed = now - self._last_frame_time
        self._last_frame_time = now
        if elapsed <= 0:
            return 0
        return max(0, int(1.0 / elapsed))

    def _maybe_publish_telemetry(self, snapshot: GestureSnapshot) -> None:
        now = time.perf_counter()
        if now - self._last_telemetry_push < 0.30:
            return
        self._last_telemetry_push = now
        self.telemetry.publish(
            TelemetrySnapshot(
                action=snapshot.action,
                fps=self._fps,
                has_hand=snapshot.has_hand,
                profile=self.profile.name,
                center_x=snapshot.center_x,
            )
        )

    def _cycle_profile(self) -> None:
        profiles = self.profile_service.list_profiles()
        if not profiles:
            return
        current = self.profile.name
        names = [profile.name for profile in profiles]
        if current not in names:
            next_name = names[0]
        else:
            next_index = (names.index(current) + 1) % len(names)
            next_name = names[next_index]

        self.profile = self.profile_service.activate_profile(next_name)
        self.logger.info("Activated profile '%s'.", self.profile.name)
        self.gesture.update_bounds(self.profile.left_bound, self.profile.right_bound)
        self.detector.close()
        self.detector = self._create_detector(self.profile)
        self.keyboard = KeyboardAdapter(self.config.key_map, cooldown_ms=self.profile.cooldown_ms)
        self.controller = GameController(
            keyboard=self.keyboard,
            window_title=self.config.game_window_title,
            auto_focus_window=self.config.auto_focus_window,
        )

    def _create_detector(self, profile: Profile) -> HandDetector:
        return HandDetector(
            model_path=self.config.model_path,
            detection_confidence=profile.detection_confidence,
            presence_confidence=profile.presence_confidence,
            tracking_confidence=profile.tracking_confidence,
        )

