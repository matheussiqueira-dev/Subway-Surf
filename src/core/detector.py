import mediapipe as mp
import mediapipe.tasks as mp_tasks
import numpy as np
import time
from src.utils.config import Config

class HandDetector:
    def __init__(self):
        self.model_path = str(Config.MODEL_PATH)
        self.landmarker = self._init_landmarker()
        self.start_time = time.perf_counter()

    def _init_landmarker(self):
        BaseOptions = mp_tasks.BaseOptions
        HandLandmarker = mp_tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp_tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp_tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=Config.DETECTION_CONFIDENCE,
            min_hand_presence_confidence=Config.DETECTION_CONFIDENCE,
            min_tracking_confidence=Config.TRACKING_CONFIDENCE,
        )
        return HandLandmarker.create_from_options(options)

    def detect(self, image):
        # Convert the frame to MediaPipe image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        timestamp_ms = int((time.perf_counter() - self.start_time) * 1000)
        
        # Perform detection
        detection_result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        return detection_result

    def get_gesture(self, landmarks):
        if not landmarks:
            return "IDLE"

        # Extract landmark positions
        lm = landmarks[0]
        fingers = self._check_fingers(lm)
        
        # Thumb, Index, Middle, Ring, Pinky
        # 4, 8, 12, 16, 20 are tips
        
        # 1. JUMP -> All fingers extended
        if all(fingers):
            return "JUMP"
        
        # 2. SLIDE -> Thumb and Pinky extended, others closed
        if fingers[0] and fingers[4] and not any(fingers[1:4]):
            return "SLIDE"
        
        # 3. HOVERBOARD -> Index and Middle extended
        if fingers[1] and fingers[2] and not any(fingers[3:5]) and not fingers[0]:
            return "HOVERBOARD"

        # Position based gestures (LANE)
        # Use center of palm (landmark 0 - Wrist or average of others)
        center_x = lm[0].x
        
        if center_x < Config.LEFT_BOUND:
            return "LEFT"
        elif center_x > Config.RIGHT_BOUND:
            return "RIGHT"
        
        return "CENTER"

    def _check_fingers(self, lm):
        fingers = []
        
        # Thumb: check if tip is to the left/right of MCP depending on hand (simplified)
        # For simplicity, we use vertical orientation if hand is upright
        if lm[4].y < lm[2].y:
            fingers.append(True)
        else:
            fingers.append(False)
            
        # 4 fingers: tip.y < pip.y
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        
        for t, p in zip(tips, pips):
            if lm[t].y < lm[p].y:
                fingers.append(True)
            else:
                fingers.append(False)
                
        return fingers

    def close(self):
        self.landmarker.close()
