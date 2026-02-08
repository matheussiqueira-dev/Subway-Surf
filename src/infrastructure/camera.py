from __future__ import annotations

import cv2


class CameraStream:
    def __init__(self, camera_index: int, width: int, height: int):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> bool:
        backends: list[int] = []
        if hasattr(cv2, "CAP_DSHOW"):
            backends.append(cv2.CAP_DSHOW)
        if hasattr(cv2, "CAP_MSMF"):
            backends.append(cv2.CAP_MSMF)
        backends.append(0)

        for backend in backends:
            cap = cv2.VideoCapture(self.camera_index, backend)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self._cap = cap
                return True
            cap.release()

        cap = cv2.VideoCapture(self.camera_index)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self._cap = cap
            return True
        cap.release()
        return False

    def is_opened(self) -> bool:
        return bool(self._cap and self._cap.isOpened())

    def read(self) -> tuple[bool, object]:
        if not self._cap:
            return False, None
        return self._cap.read()

    def release(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None

