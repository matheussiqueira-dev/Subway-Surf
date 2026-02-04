import os
from pathlib import Path

class Config:
    # Camera settings
    CAMERA_NAME = os.environ.get("CAMERA_NAME", "BRIO")
    CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", "0"))
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480

    # Paths
    ROOT_DIR = Path(__file__).parent.parent.parent
    MODEL_PATH = ROOT_DIR / "hand_landmarker.task"

    # Gesture Thresholds
    LEFT_BOUND = 0.35
    RIGHT_BOUND = 0.65
    DETECTION_CONFIDENCE = 0.7
    TRACKING_CONFIDENCE = 0.6

    # Colors (BGR)
    COLOR_PRIMARY = (255, 0, 128)  # Neon Pink
    COLOR_SECONDARY = (0, 255, 255) # Cyan
    COLOR_SUCCESS = (0, 255, 0)
    COLOR_BG = (20, 20, 20)
    COLOR_TEXT = (255, 255, 255)

    # Key Mappings
    KEYS = {
        'JUMP': 'up',
        'SLIDE': 'down',
        'LEFT': 'left',
        'RIGHT': 'right',
        'HOVERBOARD': 'space'
    }
