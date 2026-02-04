import cv2
import time
import sys
from src.core.detector import HandDetector
from src.core.controller import GameController
from src.ui.display import HUD
from src.utils.config import Config

class VirtualControllerApp:
    def __init__(self):
        print("[System] Initializing Components...")
        self.detector = HandDetector()
        self.controller = GameController()
        self.hud = HUD()
        
        self.cap = self._init_camera()
        self.prev_time = time.perf_counter()
        
    def _init_camera(self):
        # Implementation of robust camera opening
        idx = Config.CAMERA_INDEX
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
            
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
        return cap

    def run(self):
        print("[System] Running Controller...")
        self.hud.show_startup_screen()
        
        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    break
                
                # Pre-processing
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detection
                result = self.detector.detect(rgb_frame)
                
                # Logic
                current_action = "IDLE"
                landmarks = None
                
                if result and result.hand_landmarks:
                    landmarks = result.hand_landmarks
                    current_action = self.detector.get_gesture(landmarks)
                    
                    # Execute Control
                    self.controller.perform_action(current_action)
                    self.controller.reset_discrete(current_action)
                
                # FPS Calculation
                curr_time = time.perf_counter()
                fps = int(1 / (curr_time - self.prev_time))
                self.prev_time = curr_time
                
                # UI Rendering
                rendered_frame = self.hud.draw(frame, current_action, landmarks, fps)
                cv2.imshow("Subway Surfers Virtual Controller", rendered_frame)
                
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
                    
        finally:
            self.cleanup()

    def cleanup(self):
        print("[System] Shutting down...")
        self.cap.release()
        self.detector.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = VirtualControllerApp()
    app.run()

