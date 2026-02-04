from pynput.keyboard import Controller, Key
from src.utils.config import Config
try:
    import pygetwindow as gw
except ImportError:
    gw = None

class GameController:
    def __init__(self):
        self.keyboard = Controller()
        self.state = {
            'LEFT': False,
            'RIGHT': False,
            'JUMP': False,
            'SLIDE': False,
            'HOVERBOARD': False
        }
        self.window_name = "Subway Surfers" # Adjust if necessary
        
    def _focus_window(self):
        if gw:
            try:
                win = gw.getWindowsWithTitle(self.window_name)
                if win and not win[0].isActive:
                    win[0].activate()
            except Exception:
                pass

    def perform_action(self, action):
        if action == "CENTER":
            self.state['LEFT'] = False
            self.state['RIGHT'] = False
            return

        if action == "IDLE":
            return

        # Focus window on first action
        self._focus_window()

        # Discrete actions (only trigger once per gesture change)
        if action in ["JUMP", "SLIDE", "HOVERBOARD"]:
            if not self.state[action]:
                self._press(action)
                self.state[action] = True
        else:
            # Movement actions (LEFT/RIGHT)
            if action == "LEFT" and not self.state['LEFT']:
                self._press("LEFT")
                self.state['LEFT'] = True
                self.state['RIGHT'] = False
            elif action == "RIGHT" and not self.state['RIGHT']:
                self._press("RIGHT")
                self.state['RIGHT'] = True
                self.state['LEFT'] = False

    def reset_discrete(self, current_action):
        # If the current action is not JUMP, reset the jump state to allow re-trigger
        for act in ["JUMP", "SLIDE", "HOVERBOARD"]:
            if current_action != act:
                self.state[act] = False

    def _press(self, action_key):
        key_symbol = Config.KEYS.get(action_key)
        if not key_symbol:
            return

        # Map string to pynput Key
        if key_symbol == 'up': k = Key.up
        elif key_symbol == 'down': k = Key.down
        elif key_symbol == 'left': k = Key.left
        elif key_symbol == 'right': k = Key.right
        elif key_symbol == 'space': k = Key.space
        else: k = key_symbol # for characters
        
        self.keyboard.press(k)
        self.keyboard.release(k)
        print(f"[Input] Sent: {action_key}")
