import cv2
import numpy as np
from src.utils.config import Config

class HUD:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.primary_color = (255, 0, 180)  # Vivid Pink
        self.secondary_color = (0, 255, 255) # Electric Cyan
        self.overlay_opacity = 0.3

    def draw(self, frame, action, landmarks, fps):
        h, w, _ = frame.shape
        
        # 1. Create a clean base
        overlay = frame.copy()
        
        # 2. Draw Lane Indicators with Glow
        self._draw_lanes(frame, overlay, action, w, h)
        
        # 3. Draw Hand Skeleton (if landmarks)
        if landmarks:
            self._draw_hand(frame, landmarks[0], w, h)
            
        # 4. Apply Overlay
        cv2.addWeighted(overlay, self.overlay_opacity, frame, 1 - self.overlay_opacity, 0, frame)
        
        # 5. Draw UI Elements (Text & Icons)
        self._draw_status_bar(frame, action, fps, w, h)
        
        return frame

    def _draw_lanes(self, frame, overlay, action, w, h):
        lx = int(Config.LEFT_BOUND * w)
        rx = int(Config.RIGHT_BOUND * w)
        
        # Lane Boundaries
        cv2.line(frame, (lx, 0), (lx, h), (100, 100, 100), 1)
        cv2.line(frame, (rx, 0), (rx, h), (100, 100, 100), 1)
        
        # Highlight active lane
        if action == "LEFT":
            cv2.rectangle(overlay, (0, 0), (lx, h), self.secondary_color, -1)
        elif action == "RIGHT":
            cv2.rectangle(overlay, (rx, 0), (w, h), self.secondary_color, -1)
        elif action == "CENTER":
            cv2.rectangle(overlay, (lx, 0), (rx, h), self.primary_color, -1)

    def _draw_hand(self, frame, landmarks, w, h):
        # Draw connections
        # MediaPipe connections indices could be imported, but for now we draw points with glow
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            # Dot glow
            cv2.circle(frame, (cx, cy), 6, self.secondary_color, -1)
            cv2.circle(frame, (cx, cy), 2, (255, 255, 255), -1)

    def _draw_status_bar(self, frame, action, fps, w, h):
        # Top Bar Background
        cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
        cv2.line(frame, (0, 60), (w, 60), self.primary_color, 2)
        
        # Action Text
        action_color = self.secondary_color if action != "IDLE" else (150, 150, 150)
        cv2.putText(frame, f"STATUS: {action}", (20, 40), self.font, 1, action_color, 2)
        
        # FPS Indicator
        fps_text = f"{fps} FPS"
        cv2.putText(frame, fps_text, (w - 120, 40), self.font, 0.8, (255, 255, 255), 1)
        
        # Brand Footer
        footer_y = h - 20
        cv2.putText(frame, "SUBWAY SURFERS VIRTUAL CONTROLLER", (20, footer_y), self.font, 0.5, (100, 100, 100), 1)
        cv2.putText(frame, "v2.0 PRO", (w - 80, footer_y), self.font, 0.5, self.primary_color, 1)

    def show_startup_screen(self):
        banner = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(banner, "INITIALIZING SYSTEM...", (120, 240), self.font, 1, self.primary_color, 2)
        cv2.imshow("Subway Surfers Virtual Controller", banner)
        cv2.waitKey(1000)
