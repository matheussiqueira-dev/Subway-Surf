from __future__ import annotations

import math
import time

import cv2
import numpy as np

from src.domain.actions import Action
from src.domain.models import GestureSnapshot


class HUD:
    def __init__(self):
        self.font_title = cv2.FONT_HERSHEY_DUPLEX
        self.font_body = cv2.FONT_HERSHEY_SIMPLEX
        self._show_help = True

        self.palette = {
            "bg_dark": (16, 22, 27),
            "bg_soft": (26, 36, 44),
            "accent_primary": (27, 196, 255),  # amber-like in BGR
            "accent_secondary": (255, 190, 49),  # teal-like in BGR
            "success": (67, 220, 141),
            "warning": (77, 158, 255),
            "danger": (83, 84, 255),
            "text_main": (242, 245, 247),
            "text_muted": (168, 182, 193),
        }

    def toggle_help(self) -> None:
        self._show_help = not self._show_help

    def draw(
        self,
        frame,
        snapshot: GestureSnapshot,
        landmarks,
        fps: int,
        profile_name: str,
    ):
        canvas = frame.copy()
        h, w, _ = canvas.shape

        self._draw_atmosphere(canvas, w, h)
        self._draw_lanes(canvas, snapshot.action, w, h)
        if landmarks:
            self._draw_landmarks(canvas, landmarks[0], w, h)
        self._draw_header(canvas, snapshot, fps, profile_name, w)
        self._draw_footer(canvas, w, h)
        if self._show_help:
            self._draw_legend(canvas, w, h)
        return canvas

    def show_startup_screen(self, window_title: str) -> None:
        screen = np.zeros((520, 900, 3), dtype=np.uint8)
        self._draw_atmosphere(screen, 900, 520)
        cv2.putText(
            screen,
            "SUBWAY SURF CONTROL HUB",
            (120, 230),
            self.font_title,
            1.1,
            self.palette["text_main"],
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            screen,
            "Loading camera, detector and input pipeline...",
            (160, 280),
            self.font_body,
            0.7,
            self.palette["text_muted"],
            1,
            cv2.LINE_AA,
        )
        cv2.imshow(window_title, screen)
        cv2.waitKey(850)

    def _draw_atmosphere(self, image, w: int, h: int) -> None:
        # Soft gradient and top accent stripe to improve visual hierarchy.
        for y in range(h):
            blend = y / max(h - 1, 1)
            color = (
                int(self.palette["bg_dark"][0] * (1 - blend) + self.palette["bg_soft"][0] * blend),
                int(self.palette["bg_dark"][1] * (1 - blend) + self.palette["bg_soft"][1] * blend),
                int(self.palette["bg_dark"][2] * (1 - blend) + self.palette["bg_soft"][2] * blend),
            )
            cv2.line(image, (0, y), (w, y), color, 1)

        cv2.rectangle(image, (0, 0), (w, 8), self.palette["accent_secondary"], -1)

    def _draw_lanes(self, image, action: Action, w: int, h: int) -> None:
        left_x = int(w * 0.35)
        right_x = int(w * 0.65)

        overlay = image.copy()
        neutral = (54, 69, 81)
        active_left = (53, 161, 255)
        active_center = (69, 220, 169)
        active_right = (65, 120, 255)

        cv2.rectangle(overlay, (0, 64), (left_x, h - 72), neutral, -1)
        cv2.rectangle(overlay, (left_x, 64), (right_x, h - 72), neutral, -1)
        cv2.rectangle(overlay, (right_x, 64), (w, h - 72), neutral, -1)

        if action == Action.LEFT:
            cv2.rectangle(overlay, (0, 64), (left_x, h - 72), active_left, -1)
        elif action == Action.CENTER:
            cv2.rectangle(overlay, (left_x, 64), (right_x, h - 72), active_center, -1)
        elif action == Action.RIGHT:
            cv2.rectangle(overlay, (right_x, 64), (w, h - 72), active_right, -1)

        cv2.addWeighted(overlay, 0.20, image, 0.80, 0, image)

        cv2.line(image, (left_x, 64), (left_x, h - 72), (179, 201, 214), 2, cv2.LINE_AA)
        cv2.line(image, (right_x, 64), (right_x, h - 72), (179, 201, 214), 2, cv2.LINE_AA)

    def _draw_landmarks(self, image, landmarks, w: int, h: int) -> None:
        pulse = 0.6 + (0.4 * (math.sin(time.time() * 5) + 1) / 2)
        outer_radius = int(5 + pulse * 3)
        for landmark in landmarks:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(image, (x, y), outer_radius, self.palette["accent_secondary"], 1, cv2.LINE_AA)
            cv2.circle(image, (x, y), 2, self.palette["text_main"], -1, cv2.LINE_AA)

    def _draw_header(
        self,
        image,
        snapshot: GestureSnapshot,
        fps: int,
        profile_name: str,
        w: int,
    ) -> None:
        cv2.rectangle(image, (0, 0), (w, 64), (10, 14, 18), -1)

        action_text = snapshot.action.value
        action_color = self._action_color(snapshot.action)

        cv2.putText(
            image,
            "SUBWAY SURF CONTROL HUB",
            (18, 24),
            self.font_body,
            0.55,
            self.palette["text_muted"],
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            image,
            f"Action: {action_text}",
            (18, 50),
            self.font_title,
            0.85,
            action_color,
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            image,
            f"{fps:>3} FPS",
            (w - 150, 28),
            self.font_title,
            0.75,
            self.palette["text_main"],
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            image,
            f"Profile: {profile_name}",
            (w - 260, 52),
            self.font_body,
            0.55,
            self.palette["text_muted"],
            1,
            cv2.LINE_AA,
        )

    def _draw_footer(self, image, w: int, h: int) -> None:
        cv2.rectangle(image, (0, h - 48), (w, h), (10, 14, 18), -1)
        cv2.putText(
            image,
            "Q = Quit | P = Next Profile | H = Toggle Help",
            (18, h - 18),
            self.font_body,
            0.6,
            self.palette["text_muted"],
            1,
            cv2.LINE_AA,
        )

    def _draw_legend(self, image, w: int, h: int) -> None:
        card_w = 330
        x0, y0 = w - card_w - 16, 78
        y1 = min(h - 90, y0 + 220)

        overlay = image.copy()
        cv2.rectangle(overlay, (x0, y0), (x0 + card_w, y1), (12, 18, 22), -1)
        cv2.addWeighted(overlay, 0.8, image, 0.2, 0, image)
        cv2.rectangle(image, (x0, y0), (x0 + card_w, y1), (118, 146, 165), 1)

        lines = [
            "CONTROLS",
            "Open hand     -> Jump",
            "Thumb + Pinky -> Slide",
            "Index + Mid   -> Hoverboard",
            "Hand Left     -> Move left",
            "Hand Right    -> Move right",
        ]

        cv2.putText(
            image,
            lines[0],
            (x0 + 16, y0 + 26),
            self.font_title,
            0.65,
            self.palette["accent_secondary"],
            1,
            cv2.LINE_AA,
        )
        step = 31
        for idx, text in enumerate(lines[1:], start=1):
            cv2.putText(
                image,
                text,
                (x0 + 16, y0 + 26 + idx * step),
                self.font_body,
                0.58,
                self.palette["text_main"],
                1,
                cv2.LINE_AA,
            )

    def _action_color(self, action: Action) -> tuple[int, int, int]:
        if action == Action.IDLE:
            return self.palette["text_muted"]
        if action in (Action.LEFT, Action.RIGHT, Action.CENTER):
            return self.palette["warning"]
        if action == Action.JUMP:
            return self.palette["success"]
        if action == Action.SLIDE:
            return self.palette["accent_primary"]
        if action == Action.HOVERBOARD:
            return self.palette["accent_secondary"]
        return self.palette["text_main"]

