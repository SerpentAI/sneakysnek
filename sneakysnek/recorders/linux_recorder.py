from sneakysnek.recorder import Recorder

from sneakysnek.keyboard_keys import KeyboardKey
from sneakysnek.mouse_buttons import MouseButton

from sneakysnek.keyboard_event import KeyboardEvent, KeyboardEvents
from sneakysnek.mouse_event import MouseEvent, MouseEvents

import threading

import Xlib.display
import Xlib.ext
import Xlib.X
import Xlib.XK
import Xlib.protocol.rq


class LinuxRecorder(Recorder):

    def __init__(self, callback):
        self.callback = callback

        self.is_recording = False
        self.thread = None
    
        self.display_local = Xlib.display.Display()
        
        self.display_record_keyboard = Xlib.display.Display()
        self.display_record_mouse = Xlib.display.Display()
        
        self.keyboard_context = None
        self.mouse_context = None

        self.keyboard_event_thread = None
        self.mouse_event_thread = None 

    def start(self):
        self.is_recording = True

        self.keyboard_context = self._initialize_keyboard_context()
        self.mouse_context = self._initialize_mouse_context()

        self.keyboard_event_thread = threading.Thread(target=self.start_keyboard_recording, args=())
        self.keyboard_event_thread.daemon = True
        self.keyboard_event_thread.start()

        self.mouse_event_thread = threading.Thread(target=self.start_mouse_recording, args=())
        self.mouse_event_thread.daemon = True
        self.mouse_event_thread.start()

    def start_keyboard_recording(self):
        self.display_record_keyboard.record_enable_context(
            self.keyboard_context, 
            lambda r: self.event_handler(self.display_record_keyboard, r)
        )

        self.display_record_keyboard.record_free_context(self.keyboard_context)

    def start_mouse_recording(self):
        self.display_record_mouse.record_enable_context(
            self.mouse_context, 
            lambda r: self.event_handler(self.display_record_mouse, r)
        )

        self.display_record_mouse.record_free_context(self.mouse_context)
        
    def stop(self):
        self.display_local.record_disable_context(self.keyboard_context)
        self.display_local.record_disable_context(self.mouse_context)

        self.display_local.flush()

        self.display_record_keyboard.close()
        self.display_record_mouse.close()
        self.display_local.close()

        self.thread.join()

        self.is_recording = False

    def event_handler(self, display, reply):
        data = reply.data
        
        while len(data):
            event, data = Xlib.protocol.rq.EventField(None).parse_binary_value(
                data, 
                display.display, 
                None, 
                None
            )

            if event.type in [Xlib.X.KeyPress, Xlib.X.KeyRelease]:
                index = self._shift_to_index(self.display_local, event.state)
                scan_code = self._keycode_to_scan_code(self.display_local, event.detail, index)

                if scan_code in keyboard_scan_code_mapping:
                    keyboard_key = keyboard_scan_code_mapping[scan_code]
                else:
                    return None

                self.callback(KeyboardEvent(KeyboardEvents.DOWN if event.type == Xlib.X.KeyPress else KeyboardEvents.UP, keyboard_key))
            elif event.type == Xlib.X.ButtonPress:
                if event.detail in mouse_button_mapping:
                    button = mouse_button_mapping[event.detail]

                    x = event.root_x
                    y = event.root_y

                    self.callback(MouseEvent(MouseEvents.CLICK, button=button, direction="DOWN", x=x, y=y))
            elif event.type == Xlib.X.ButtonRelease:
                if event.detail in mouse_button_mapping:
                    button = mouse_button_mapping[event.detail]

                    x = event.root_x
                    y = event.root_y

                    self.callback(MouseEvent(MouseEvents.CLICK, button=button, direction="UP", x=x, y=y))
                elif event.detail in [4, 5]:
                    direction = "UP" if event.detail == 4 else "DOWN"

                    x = event.root_x
                    y = event.root_y
                    
                    self.callback(MouseEvent(MouseEvents.SCROLL, direction=direction, velocity=1, x=x, y=y))
            elif event.type == Xlib.X.MotionNotify:
                self.callback(MouseEvent(MouseEvents.MOVE, x=event.root_x, y=event.root_y))

    def _initialize_keyboard_context(self):
        return self.display_record_keyboard.record_create_context(
            0,
            [Xlib.ext.record.AllClients],
            [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (
                        Xlib.X.KeyPress,
                        Xlib.X.KeyRelease
                    ),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
            }]
        )
    
    def _initialize_mouse_context(self):
        return self.display_record_mouse.record_create_context(
            0,
            [Xlib.ext.record.AllClients],
            [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (
                        Xlib.X.ButtonPressMask,
                        Xlib.X.ButtonReleaseMask
                    ),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
            }]
        )

    def _shift_to_index(self, display, shift):
        return ((1 if shift & 1 else 0) + (2 if shift & self._alt_gr_mask(display) else 0))

    def _alt_gr_mask(self, display):
        if not hasattr(display, "__altgr_mask"):
            display.__altgr_mask = self._find_mask(display, "Mode_switch")
        
        return display.__altgr_mask

    def _find_mask(self, display, symbol):
        modifier_keycode = display.keysym_to_keycode(Xlib.XK.string_to_keysym(symbol))

        for index, keycodes in enumerate(display.get_modifier_mapping()):
            for keycode in keycodes:
                if keycode == modifier_keycode:
                    return 1 << index

        return 0

    def _keycode_to_scan_code(self, display, keycode, index):
        scan_code = display.keycode_to_keysym(keycode, index)

        if scan_code:
            return scan_code
        elif index & 0x2:
            return self._keycode_to_scan_code(display, keycode, index & ~0x2)
        elif index & 0x1:
            return self._keycode_to_scan_code(display, keycode, index & ~0x1)
        else:
            return 0

    @classmethod
    def record(cls, callback):
        recorder = cls(callback)

        recorder.thread = threading.Thread(target=recorder.start, args=())
        recorder.thread.daemon = True
        recorder.thread.start()

        return recorder

keyboard_scan_code_mapping = {
    65307: KeyboardKey.KEY_ESCAPE,
    65470: KeyboardKey.KEY_F1,
    65471: KeyboardKey.KEY_F2,
    65472: KeyboardKey.KEY_F3,
    65473: KeyboardKey.KEY_F4,
    65474: KeyboardKey.KEY_F5,
    65475: KeyboardKey.KEY_F6,
    65476: KeyboardKey.KEY_F7,
    65477: KeyboardKey.KEY_F8,
    65478: KeyboardKey.KEY_F9,
    65479: KeyboardKey.KEY_F10,
    65480: KeyboardKey.KEY_F11,
    65481: KeyboardKey.KEY_F12,
    65377: KeyboardKey.KEY_PRINT_SCREEN,
    65300: KeyboardKey.KEY_SCROLL_LOCK,
    65299: KeyboardKey.KEY_PAUSE,
    96: KeyboardKey.KEY_GRAVE,
    49: KeyboardKey.KEY_1,
    50: KeyboardKey.KEY_2,
    51: KeyboardKey.KEY_3,
    52: KeyboardKey.KEY_4,
    53: KeyboardKey.KEY_5,
    54: KeyboardKey.KEY_6,
    55: KeyboardKey.KEY_7,
    56: KeyboardKey.KEY_8,
    57: KeyboardKey.KEY_9,
    48: KeyboardKey.KEY_0,
    45: KeyboardKey.KEY_MINUS,
    61: KeyboardKey.KEY_EQUALS,
    65288: KeyboardKey.KEY_BACKSPACE,
    65379: KeyboardKey.KEY_INSERT,
    65360: KeyboardKey.KEY_HOME,
    65365: KeyboardKey.KEY_PAGE_UP,
    65407: KeyboardKey.KEY_NUMLOCK,
    65455: KeyboardKey.KEY_NUMPAD_DIVIDE,
    65450: KeyboardKey.KEY_NUMPAD_MULTIPLY,
    65453: KeyboardKey.KEY_NUMPAD_SUBTRACT,
    65289: KeyboardKey.KEY_TAB,
    113: KeyboardKey.KEY_Q,
    119: KeyboardKey.KEY_W,
    101: KeyboardKey.KEY_E,
    114: KeyboardKey.KEY_R,
    116: KeyboardKey.KEY_T,
    121: KeyboardKey.KEY_Y,
    117: KeyboardKey.KEY_U,
    105: KeyboardKey.KEY_I,
    111: KeyboardKey.KEY_O,
    112: KeyboardKey.KEY_P,
    91: KeyboardKey.KEY_LEFT_BRACKET,
    93: KeyboardKey.KEY_RIGHT_BRACKET,
    92: KeyboardKey.KEY_BACKSLASH,
    65535: KeyboardKey.KEY_DELETE,
    65367: KeyboardKey.KEY_END,
    65366: KeyboardKey.KEY_PAGE_DOWN,
    65429: KeyboardKey.KEY_NUMPAD_7,
    65431: KeyboardKey.KEY_NUMPAD_8,
    65434: KeyboardKey.KEY_NUMPAD_9,
    65451: KeyboardKey.KEY_NUMPAD_ADD,
    65509: KeyboardKey.KEY_CAPSLOCK,
    97: KeyboardKey.KEY_A,
    115: KeyboardKey.KEY_S,
    100: KeyboardKey.KEY_D,
    102: KeyboardKey.KEY_F,
    103: KeyboardKey.KEY_G,
    104: KeyboardKey.KEY_H,
    106: KeyboardKey.KEY_J,
    107: KeyboardKey.KEY_K,
    108: KeyboardKey.KEY_L,
    59: KeyboardKey.KEY_SEMICOLON,
    39: KeyboardKey.KEY_APOSTROPHE,
    65293: KeyboardKey.KEY_RETURN,
    65430: KeyboardKey.KEY_NUMPAD_4,
    65437: KeyboardKey.KEY_NUMPAD_5,
    65432: KeyboardKey.KEY_NUMPAD_6,
    65505: KeyboardKey.KEY_LEFT_SHIFT,
    122: KeyboardKey.KEY_Z,
    120: KeyboardKey.KEY_X,
    99: KeyboardKey.KEY_C,
    118: KeyboardKey.KEY_V,
    98: KeyboardKey.KEY_B,
    110: KeyboardKey.KEY_N,
    109: KeyboardKey.KEY_M,
    44: KeyboardKey.KEY_COMMA,
    46: KeyboardKey.KEY_PERIOD,
    47: KeyboardKey.KEY_SLASH,
    65506: KeyboardKey.KEY_RIGHT_SHIFT,
    65362: KeyboardKey.KEY_UP,
    65436: KeyboardKey.KEY_NUMPAD_1,
    65433: KeyboardKey.KEY_NUMPAD_2,
    65435: KeyboardKey.KEY_NUMPAD_3,
    65421: KeyboardKey.KEY_NUMPAD_RETURN,
    65507: KeyboardKey.KEY_LEFT_CTRL,
    65513: KeyboardKey.KEY_LEFT_ALT,
    32: KeyboardKey.KEY_SPACE,
    65514: KeyboardKey.KEY_RIGHT_ALT,
    65508: KeyboardKey.KEY_RIGHT_CTRL,
    65361: KeyboardKey.KEY_LEFT,
    65364: KeyboardKey.KEY_DOWN,
    65363: KeyboardKey.KEY_RIGHT,
    65438: KeyboardKey.KEY_NUMPAD_0,
    65439: KeyboardKey.KEY_NUMPAD_PERIOD,
    65515: KeyboardKey.KEY_LEFT_WINDOWS,
    65516: KeyboardKey.KEY_RIGHT_WINDOWS
}

mouse_button_mapping = {
    1 : MouseButton.LEFT,
    2 : MouseButton.MIDDLE,
    3 : MouseButton.RIGHT
}