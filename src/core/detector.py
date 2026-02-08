from __future__ import annotations

import time
from pathlib import Path

import mediapipe as mp
import mediapipe.tasks as mp_tasks


class HandDetector:
    def __init__(
        self,
        model_path: Path,
        detection_confidence: float,
        presence_confidence: float,
        tracking_confidence: float,
    ):
        if not model_path.exists():
            raise FileNotFoundError(f"Hand model file not found: {model_path}")
        self.model_path = model_path
        self.detection_confidence = detection_confidence
        self.presence_confidence = presence_confidence
        self.tracking_confidence = tracking_confidence
        self._start_time = time.perf_counter()
        self._landmarker = self._create_landmarker()

    def _create_landmarker(self):
        vision = mp_tasks.vision
        options = vision.HandLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=str(self.model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=self.detection_confidence,
            min_hand_presence_confidence=self.presence_confidence,
            min_tracking_confidence=self.tracking_confidence,
        )
        return vision.HandLandmarker.create_from_options(options)

    def detect(self, rgb_image):
        timestamp_ms = int((time.perf_counter() - self._start_time) * 1000)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        return self._landmarker.detect_for_video(mp_image, timestamp_ms)

    def close(self) -> None:
        self._landmarker.close()

