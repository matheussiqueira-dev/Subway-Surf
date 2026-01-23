import cv2
import mediapipe as mp
import mediapipe.tasks as mp_tasks
from pynput.keyboard import Key, Controller
import time
import os
from pathlib import Path
import sys

# -------------------------------------------
# INITIAL SETUP
# -------------------------------------------

keyboard = Controller()

CAMERA_NAME = os.environ.get("CAMERA_NAME", "BRIO")
CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", "0"))

MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")
if not MODEL_PATH.exists():
    print(f"Model file not found: {MODEL_PATH}")
    sys.exit(1)

model_buffer = MODEL_PATH.read_bytes()

vision = mp_tasks.vision
options = vision.HandLandmarkerOptions(
    base_options=mp_tasks.BaseOptions(model_asset_buffer=model_buffer),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
landmarker = vision.HandLandmarker.create_from_options(options)

def pick_camera_index():
    if CAMERA_NAME:
        try:
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            devices = graph.get_input_devices()
            for idx, name in enumerate(devices):
                if CAMERA_NAME.lower() in name.lower():
                    print(f"Using camera: {name} (index {idx})")
                    return idx
            if devices:
                print(f"Camera '{CAMERA_NAME}' not found. Available: {', '.join(devices)}")
        except Exception as exc:
            print(f"Could not enumerate cameras by name. Falling back to CAMERA_INDEX. ({exc})")
    return CAMERA_INDEX

def open_camera(index):
    backends = []
    if hasattr(cv2, "CAP_DSHOW"):
        backends.append(cv2.CAP_DSHOW)
    if hasattr(cv2, "CAP_MSMF"):
        backends.append(cv2.CAP_MSMF)
    backends.append(0)

    for backend in backends:
        cap_try = cv2.VideoCapture(index, backend)
        if cap_try.isOpened():
            return cap_try
    return cv2.VideoCapture(index)

camera_index = pick_camera_index()
print(f"Opening camera index: {camera_index}")
cap = open_camera(camera_index)
if not cap.isOpened() and camera_index != CAMERA_INDEX:
    print(f"Falling back to CAMERA_INDEX: {CAMERA_INDEX}")
    cap = open_camera(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Could not open camera. Close other apps using the webcam and try again.")
    landmarker.close()
    sys.exit(1)

pTime = time.perf_counter()
start_time = time.perf_counter()
current_action = "IDLE"

# -------------------------------------------
# STATE MEMORY (PREVENT REPEAT)
# -------------------------------------------

gesture_state = {
    'left': False,
    'right': False,
    'jump': False,
    'slide': False,
    'hover': False
}

# -------------------------------------------
# LANE BOUNDARIES
# -------------------------------------------

LEFT_BOUND = 0.35
RIGHT_BOUND = 0.65

# -------------------------------------------
# LANDMARK INDEXES
# -------------------------------------------

THUMB_TIP = 4
THUMB_MCP = 2
INDEX_TIP = 8
INDEX_PIP = 6
MIDDLE_TIP = 12
MIDDLE_PIP = 10
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18

# -------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------

def press_and_release(key):
    keyboard.press(key)
    keyboard.release(key)

def count_extended_fingers(landmarks):
    fingers = [False] * 5

    # Thumb
    if landmarks[THUMB_TIP].y < landmarks[THUMB_MCP].y:
        fingers[0] = True

    # Other fingers
    if landmarks[INDEX_TIP].y < landmarks[INDEX_PIP].y:
        fingers[1] = True
    if landmarks[MIDDLE_TIP].y < landmarks[MIDDLE_PIP].y:
        fingers[2] = True
    if landmarks[RING_TIP].y < landmarks[RING_PIP].y:
        fingers[3] = True
    if landmarks[PINKY_TIP].y < landmarks[PINKY_PIP].y:
        fingers[4] = True

    return fingers

def draw_lanes(img, w, h):
    lx = int(LEFT_BOUND * w)
    rx = int(RIGHT_BOUND * w)
    cv2.line(img, (lx, 0), (lx, h), (200, 200, 200), 2)
    cv2.line(img, (rx, 0), (rx, h), (200, 200, 200), 2)

def draw_landmarks(img, hand_landmarks, w, h):
    for lm in hand_landmarks:
        cx = int(lm.x * w)
        cy = int(lm.y * h)
        cv2.circle(img, (cx, cy), 4, (0, 255, 0), -1)

# -------------------------------------------
# MAIN LOOP
# -------------------------------------------

print("Starting Subway Surfers Virtual Controller...")
print("Controls:")
print("  - Open hand (5 fingers) -> JUMP")
print("  - Thumb + Pinky -> SLIDE")
print("  - Index + Middle -> HOVERBOARD")
print("  - Hand on left side -> MOVE LEFT")
print("  - Hand on right side -> MOVE RIGHT")
print("Press 'q' to quit")
print()

try:
    read_failures = 0
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            read_failures += 1
            if read_failures > 30:
                print("Camera read failed. Make sure the correct webcam is selected and not in use.")
                break
            continue
        read_failures = 0

        image = cv2.flip(image, 1)
        h, w, _ = image.shape

        draw_lanes(image, w, h)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.perf_counter() - start_time) * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        current_action = "IDLE"

        if result and result.hand_landmarks:
            hand = result.hand_landmarks[0]

            draw_landmarks(image, hand, w, h)

            thumb = hand[THUMB_TIP]
            index = hand[INDEX_TIP]
            center_x = (thumb.x + index.x) / 2

            fingers = count_extended_fingers(hand)

            # -----------------------------
            # JUMP → OPEN PALM
            # -----------------------------
            if all(fingers):
                if not gesture_state['jump']:
                    press_and_release(Key.up)
                    gesture_state['jump'] = True
                current_action = "JUMP"
            else:
                gesture_state['jump'] = False

            # -----------------------------
            # SLIDE → THUMB + PINKY
            # -----------------------------
            if fingers[0] and fingers[4] and not fingers[1] and not fingers[2] and not fingers[3]:
                if not gesture_state['slide']:
                    press_and_release(Key.down)
                    gesture_state['slide'] = True
                current_action = "SLIDE"
            else:
                gesture_state['slide'] = False

            # -----------------------------
            # HOVERBOARD → INDEX + MIDDLE
            # -----------------------------
            if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
                if not gesture_state['hover']:
                    press_and_release(Key.space)
                    gesture_state['hover'] = True
                current_action = "HOVERBOARD"
            else:
                gesture_state['hover'] = False

            # -----------------------------
            # LEFT / RIGHT → HAND POSITION
            # -----------------------------
            if center_x < LEFT_BOUND:
                if not gesture_state['left']:
                    press_and_release(Key.left)
                    gesture_state['left'] = True
                gesture_state['right'] = False
                current_action = "LEFT"

            elif center_x > RIGHT_BOUND:
                if not gesture_state['right']:
                    press_and_release(Key.right)
                    gesture_state['right'] = True
                gesture_state['left'] = False
                current_action = "RIGHT"

            else:
                gesture_state['left'] = False
                gesture_state['right'] = False
                if current_action == "IDLE":
                    current_action = "CENTER"

            cv2.putText(image, f"Fingers: {fingers}", (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # FPS
        cTime = time.perf_counter()
        fps = int(1 / (cTime - pTime)) if cTime != pTime else 0
        pTime = cTime

        cv2.putText(image, f"FPS: {fps}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        cv2.putText(image, f"Action: {current_action}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Subway Surfers Virtual Controller", image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    landmarker.close()
    cv2.destroyAllWindows()
