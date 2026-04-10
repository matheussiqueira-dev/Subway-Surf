from __future__ import annotations

import cv2
import numpy as np


class CameraStream:
    """OpenCV-backed video capture with multi-backend fallback."""

    def __init__(self, camera_index: int, width: int, height: int) -> None:
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> bool:
        """Try DirectShow → Media Foundation → default backend in order.

        Returns True as soon as one backend opens successfully.
        """
        backends: list[int] = []
        if hasattr(cv2, "CAP_DSHOW"):
            backends.append(cv2.CAP_DSHOW)
        if hasattr(cv2, "CAP_MSMF"):
            backends.append(cv2.CAP_MSMF)

        for backend in backends:
            cap = cv2.VideoCapture(self.camera_index, backend)
            if cap.isOpened():
                self._apply_resolution(cap)
                self._cap = cap
                return True
            cap.release()

        # Platform-neutral fallback (Linux V4L2, macOS AVFoundation, etc.)
        cap = cv2.VideoCapture(self.camera_index)
        if cap.isOpened():
            self._apply_resolution(cap)
            self._cap = cap
            return True
        cap.release()
        return False

    def _apply_resolution(self, cap: cv2.VideoCapture) -> None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def is_opened(self) -> bool:
        return bool(self._cap and self._cap.isOpened())

    def read(self) -> tuple[bool, np.ndarray | None]:
        """Read the next frame.

        Returns (True, frame) on success or (False, None) when the device
        is not open or the read fails.
        """
        if not self._cap:
            return False, None
        ok, frame = self._cap.read()
        return ok, frame if ok else None

    def release(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None
