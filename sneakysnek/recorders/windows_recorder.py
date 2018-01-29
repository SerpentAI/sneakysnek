from sneakysnek.recorder import Recorder

from sneakysnek.keyboard_keys import KeyboardKey
from sneakysnek.mouse_buttons import MouseButton

from sneakysnek.keyboard_event import KeyboardEvent, KeyboardEvents
from sneakysnek.mouse_event import MouseEvent, MouseEvents

import ctypes
from ctypes import windll, wintypes

import threading
import atexit


class WindowsRecorder(Recorder):

    def __init__(self, callback):
        self.callback = callback

        self.is_recording = False
        self.thread = None

        self.thread_id = None

        self.keyboard_hook = None
        self.mouse_hook = None

    def start(self):
        self.is_recording = True
        self.thread_id = windll.kernel32.GetCurrentThreadId()

        self.register_hooks()
        self.listen()

    def stop(self):
        PostThreadMessage(self.thread_id, 0x0401, 0, 0)

        if self.keyboard_hook is not None:
            UnhookWindowsHookEx(self.keyboard_hook)

        if self.mouse_hook is not None:
            UnhookWindowsHookEx(self.mouse_hook)

        self.is_recording = False

    def event_handler(self, event):
        self.callback(event)

    def register_hooks(self):
        self._register_keyboard_hook()
        self._register_mouse_hook()

    def listen(self):
        while True:
            message = wintypes.MSG()
            message_pointer = ctypes.byref(message)

            if GetMessage(message_pointer, None, 0, 0) <= 0 or message.message == 0x0401:
                break

    def _register_keyboard_hook(self):
        def low_level_callback(code, wparam, lparam):
            scan_code = (lparam.contents.scanCode + (lparam.contents.flags & 1) * 1024)

            if scan_code in keyboard_scan_code_mapping and wparam in [256, 257]:
                    self.event_handler(KeyboardEvent(
                        KeyboardEvents.DOWN if wparam == 256 else KeyboardEvents.UP,
                        keyboard_scan_code_mapping[scan_code]
                    ))

            return CallNextHookEx(None, code, wparam, lparam)

        callback = LowLevelKeyboardProc(low_level_callback)

        self.keyboard_hook = SetWindowsHookEx(13, callback, None, None)
        atexit.register(UnhookWindowsHookEx, callback)

    def _register_mouse_hook(self):
        def low_level_callback(code, wparam, lparam):
            if wparam == 512:
                self.event_handler(MouseEvent(
                    MouseEvents.MOVE,
                    x=lparam.contents.pt.x,
                    y=lparam.contents.pt.y
                ))
            elif wparam == 522:
                self.event_handler(MouseEvent(
                    MouseEvents.SCROLL,
                    direction="UP" if (wintypes.SHORT(lparam.contents.mouseData >> 16).value // 120) == 1 else "DOWN",
                    velocity=1,
                    x=lparam.contents.pt.x,
                    y=lparam.contents.pt.y
                ))
            elif wparam in [513, 514, 516, 517, 519, 520]:
                self.event_handler(MouseEvent(
                    MouseEvents.CLICK,
                    button=mouse_button_mapping[wparam],
                    direction="DOWN" if wparam in [513, 516, 519] else "UP",
                    x=lparam.contents.pt.x,
                    y=lparam.contents.pt.y
                ))

            return CallNextHookEx(None, code, wparam, lparam)

        callback = LowLevelMouseProc(low_level_callback)

        self.mouse_hook = SetWindowsHookEx(14, callback, None, None)
        atexit.register(UnhookWindowsHookEx, callback)

    @classmethod
    def record(cls, callback):
        recorder = cls(callback)

        recorder.thread = threading.Thread(target=recorder.start, args=())
        recorder.thread.daemon = True
        recorder.thread.start()

        return recorder


keyboard_scan_code_mapping = {
    1: KeyboardKey.KEY_ESCAPE,
    59: KeyboardKey.KEY_F1,
    60: KeyboardKey.KEY_F2,
    61: KeyboardKey.KEY_F3,
    62: KeyboardKey.KEY_F4,
    63: KeyboardKey.KEY_F5,
    64: KeyboardKey.KEY_F6,
    65: KeyboardKey.KEY_F7,
    66: KeyboardKey.KEY_F8,
    67: KeyboardKey.KEY_F9,
    68: KeyboardKey.KEY_F10,
    87: KeyboardKey.KEY_F11,
    88: KeyboardKey.KEY_F12,
    1079: KeyboardKey.KEY_PRINT_SCREEN,
    70: KeyboardKey.KEY_SCROLL_LOCK,
    69: KeyboardKey.KEY_PAUSE,
    41: KeyboardKey.KEY_GRAVE,
    2: KeyboardKey.KEY_1,
    3: KeyboardKey.KEY_2,
    4: KeyboardKey.KEY_3,
    5: KeyboardKey.KEY_4,
    6: KeyboardKey.KEY_5,
    7: KeyboardKey.KEY_6,
    8: KeyboardKey.KEY_7,
    9: KeyboardKey.KEY_8,
    10: KeyboardKey.KEY_9,
    11: KeyboardKey.KEY_0,
    12: KeyboardKey.KEY_MINUS,
    13: KeyboardKey.KEY_EQUALS,
    14: KeyboardKey.KEY_BACKSPACE,
    1106: KeyboardKey.KEY_INSERT,
    1095: KeyboardKey.KEY_HOME,
    1097: KeyboardKey.KEY_PAGE_UP,
    1093: KeyboardKey.KEY_NUMLOCK,
    1077: KeyboardKey.KEY_NUMPAD_DIVIDE,
    55: KeyboardKey.KEY_NUMPAD_MULTIPLY,
    74: KeyboardKey.KEY_NUMPAD_SUBTRACT,
    15: KeyboardKey.KEY_TAB,
    16: KeyboardKey.KEY_Q,
    17: KeyboardKey.KEY_W,
    18: KeyboardKey.KEY_E,
    19: KeyboardKey.KEY_R,
    20: KeyboardKey.KEY_T,
    21: KeyboardKey.KEY_Y,
    22: KeyboardKey.KEY_U,
    23: KeyboardKey.KEY_I,
    24: KeyboardKey.KEY_O,
    25: KeyboardKey.KEY_P,
    26: KeyboardKey.KEY_LEFT_BRACKET,
    27: KeyboardKey.KEY_RIGHT_BRACKET,
    43: KeyboardKey.KEY_BACKSLASH,
    1107: KeyboardKey.KEY_DELETE,
    1103: KeyboardKey.KEY_END,
    1105: KeyboardKey.KEY_PAGE_DOWN,
    71: KeyboardKey.KEY_NUMPAD_7,
    72: KeyboardKey.KEY_NUMPAD_8,
    73: KeyboardKey.KEY_NUMPAD_9,
    78: KeyboardKey.KEY_NUMPAD_ADD,
    58: KeyboardKey.KEY_CAPSLOCK,
    30: KeyboardKey.KEY_A,
    31: KeyboardKey.KEY_S,
    32: KeyboardKey.KEY_D,
    33: KeyboardKey.KEY_F,
    34: KeyboardKey.KEY_G,
    35: KeyboardKey.KEY_H,
    36: KeyboardKey.KEY_J,
    37: KeyboardKey.KEY_K,
    38: KeyboardKey.KEY_L,
    39: KeyboardKey.KEY_SEMICOLON,
    40: KeyboardKey.KEY_APOSTROPHE,
    28: KeyboardKey.KEY_RETURN,
    75: KeyboardKey.KEY_NUMPAD_4,
    76: KeyboardKey.KEY_NUMPAD_5,
    77: KeyboardKey.KEY_NUMPAD_6,
    42: KeyboardKey.KEY_LEFT_SHIFT,
    44: KeyboardKey.KEY_Z,
    45: KeyboardKey.KEY_X,
    46: KeyboardKey.KEY_C,
    47: KeyboardKey.KEY_V,
    48: KeyboardKey.KEY_B,
    49: KeyboardKey.KEY_N,
    50: KeyboardKey.KEY_M,
    51: KeyboardKey.KEY_COMMA,
    52: KeyboardKey.KEY_PERIOD,
    53: KeyboardKey.KEY_SLASH,
    1078: KeyboardKey.KEY_RIGHT_SHIFT,
    1096: KeyboardKey.KEY_UP,
    79: KeyboardKey.KEY_NUMPAD_1,
    80: KeyboardKey.KEY_NUMPAD_2,
    81: KeyboardKey.KEY_NUMPAD_3,
    1052: KeyboardKey.KEY_NUMPAD_RETURN,
    29: KeyboardKey.KEY_LEFT_CTRL,
    56: KeyboardKey.KEY_LEFT_ALT,
    57: KeyboardKey.KEY_SPACE,
    1080: KeyboardKey.KEY_RIGHT_ALT,
    1053: KeyboardKey.KEY_RIGHT_CTRL,
    1099: KeyboardKey.KEY_LEFT,
    1104: KeyboardKey.KEY_DOWN,
    1101: KeyboardKey.KEY_RIGHT,
    82: KeyboardKey.KEY_NUMPAD_0,
    83: KeyboardKey.KEY_NUMPAD_PERIOD,
    91: KeyboardKey.KEY_LEFT_WINDOWS,
    1116: KeyboardKey.KEY_RIGHT_WINDOWS,
    1117: KeyboardKey.KEY_APP_MENU
}


mouse_button_mapping = {
    513: MouseButton.LEFT,
    514: MouseButton.LEFT,
    516: MouseButton.RIGHT,
    517: MouseButton.RIGHT,
    519: MouseButton.MIDDLE,
    520: MouseButton.MIDDLE
}


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p)
    ]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p)
    ]

LPMSG = ctypes.POINTER(wintypes.MSG)

LowLevelKeyboardProc = ctypes.CFUNCTYPE(wintypes.INT, wintypes.WPARAM, wintypes.LPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT))
LowLevelMouseProc = ctypes.CFUNCTYPE(wintypes.INT, wintypes.WPARAM, wintypes.LPARAM, ctypes.POINTER(MSLLHOOKSTRUCT))

GetMessage = windll.user32.GetMessageW
PostThreadMessage = windll.user32.PostThreadMessageW

SetWindowsHookEx = windll.user32.SetWindowsHookExA
UnhookWindowsHookEx = windll.user32.UnhookWindowsHookEx
CallNextHookEx = windll.user32.CallNextHookEx
