from sneakysnek.recorder import Recorder

from sneakysnek.keyboard_keys import KeyboardKey
from sneakysnek.mouse_buttons import MouseButton

from sneakysnek.keyboard_event import KeyboardEvent, KeyboardEvents
from sneakysnek.mouse_event import MouseEvent, MouseEvents

import threading
import Quartz


mouse_click_down_events = [Quartz.kCGEventLeftMouseDown, Quartz.kCGEventRightMouseDown, Quartz.kCGEventOtherMouseDown]
mouse_click_up_events = [Quartz.kCGEventLeftMouseUp, Quartz.kCGEventRightMouseUp, Quartz.kCGEventOtherMouseUp]


class MacOSRecorder(Recorder):

    def __init__(self, callback):
        self.callback = callback

        self.is_recording = False
        self.thread = None

        self.event_tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) |
            Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged) |
            Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseUp) |
            Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseUp) |
            Quartz.CGEventMaskBit(Quartz.kCGEventOtherMouseDown) |
            Quartz.CGEventMaskBit(Quartz.kCGEventOtherMouseUp) |
            Quartz.CGEventMaskBit(Quartz.kCGEventMouseMoved) |
            Quartz.CGEventMaskBit(Quartz.kCGEventScrollWheel),
            self.event_handler,
            None
        )

    def start(self):
        self.is_recording = True

        loop_source = Quartz.CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
        loop = Quartz.CFRunLoopGetCurrent()

        Quartz.CFRunLoopAddSource(loop, loop_source, Quartz.kCFRunLoopDefaultMode)
        Quartz.CGEventTapEnable(self.event_tap, True)

        while self.is_recording:
            Quartz.CFRunLoopRunInMode(Quartz.kCFRunLoopDefaultMode, 5, False)

    def stop(self):
        self.is_recording = False

    def event_handler(self, proxy, event_type, event, *args):
        if event_type in [Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp]:
            scan_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            keyboard_key = keyboard_scan_code_mapping.get(scan_code)

            if keyboard_key is None:
                return event

            keyboard_event = KeyboardEvents.UP if event_type == Quartz.kCGEventKeyUp else KeyboardEvents.DOWN

            self.callback(KeyboardEvent(keyboard_event, keyboard_key))
        elif event_type == Quartz.kCGEventFlagsChanged:
            scan_code = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            keyboard_key = keyboard_scan_code_mapping.get(scan_code)

            if keyboard_key is None:
                return event

            flags = Quartz.CGEventGetFlags(event)

            if scan_code in [56, 60] and (flags & Quartz.kCGEventFlagMaskShift):
                keyboard_event = KeyboardEvents.DOWN
            elif scan_code == 57 and (flags & Quartz.kCGEventFlagMaskAlphaShift):
                keyboard_event = KeyboardEvents.DOWN
            elif scan_code in [58, 61] and (flags & Quartz.kCGEventFlagMaskAlternate):
                keyboard_event = KeyboardEvents.DOWN
            elif scan_code in [59, 62] and (flags & Quartz.kCGEventFlagMaskControl):
                keyboard_event = KeyboardEvents.DOWN
            elif scan_code in [54, 55] and (flags & Quartz.kCGEventFlagMaskCommand):
                keyboard_event = KeyboardEvents.DOWN
            else:
                keyboard_event = KeyboardEvents.UP

            self.callback(KeyboardEvent(keyboard_event, keyboard_key))
        elif event_type in (mouse_click_down_events + mouse_click_up_events):
            direction = "DOWN" if event_type in mouse_click_down_events else "UP"

            x, y = [int(i) for i in Quartz.CGEventGetLocation(event)]

            if event_type in mouse_button_mapping:
                button = mouse_button_mapping[event_type]
            else:
                button_number = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGMouseEventButtonNumber)

                if (button_number + 1024) in mouse_button_mapping:
                    button = mouse_button_mapping[button_number + 1024]
                else:
                    return event

            self.callback(MouseEvent(MouseEvents.CLICK, button=button, direction=direction, x=x, y=y))
        elif event_type == Quartz.kCGEventScrollWheel:
            x, y = [int(i) for i in Quartz.CGEventGetLocation(event)]

            velocity = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis1)
            direction = "UP" if velocity > 0 else "DOWN"

            self.callback(MouseEvent(MouseEvents.SCROLL, direction=direction, velocity=abs(velocity), x=x, y=y))
        elif event_type == Quartz.kCGEventMouseMoved:
            x, y = [int(i) for i in Quartz.CGEventGetLocation(event)]

            self.callback(MouseEvent(MouseEvents.MOVE, x=x, y=y))
        else:
            return event

        return event

    @classmethod
    def record(cls, callback):
        recorder = cls(callback)

        recorder.thread = threading.Thread(target=recorder.start, args=())
        recorder.thread.daemon = True
        recorder.thread.start()

        return recorder


keyboard_scan_code_mapping = {
    0x35: KeyboardKey.KEY_ESCAPE,
    0x7A: KeyboardKey.KEY_F1,
    0x78: KeyboardKey.KEY_F2,
    0x63: KeyboardKey.KEY_F3,
    0x76: KeyboardKey.KEY_F4,
    0x60: KeyboardKey.KEY_F5,
    0x61: KeyboardKey.KEY_F6,
    0x62: KeyboardKey.KEY_F7,
    0x64: KeyboardKey.KEY_F8,
    0x65: KeyboardKey.KEY_F9,
    0x6D: KeyboardKey.KEY_F10,
    0x67: KeyboardKey.KEY_F11,
    0x6F: KeyboardKey.KEY_F12,
    0x69: KeyboardKey.KEY_PRINT_SCREEN,
    0x6B: KeyboardKey.KEY_SCROLL_LOCK,
    0x71: KeyboardKey.KEY_PAUSE,
    0x32: KeyboardKey.KEY_GRAVE,
    0x12: KeyboardKey.KEY_1,
    0x13: KeyboardKey.KEY_2,
    0x14: KeyboardKey.KEY_3,
    0x15: KeyboardKey.KEY_4,
    0x17: KeyboardKey.KEY_5,
    0x16: KeyboardKey.KEY_6,
    0x1A: KeyboardKey.KEY_7,
    0x1C: KeyboardKey.KEY_8,
    0x19: KeyboardKey.KEY_9,
    0x1D: KeyboardKey.KEY_0,
    0x1B: KeyboardKey.KEY_MINUS,
    0x18: KeyboardKey.KEY_EQUALS,
    0x33: KeyboardKey.KEY_BACKSPACE,
    0x72: KeyboardKey.KEY_INSERT,
    0x73: KeyboardKey.KEY_HOME,
    0x74: KeyboardKey.KEY_PAGE_UP,
    0x47: KeyboardKey.KEY_NUMLOCK,
    0x4B: KeyboardKey.KEY_NUMPAD_DIVIDE,
    0x43: KeyboardKey.KEY_NUMPAD_MULTIPLY,
    0x4E: KeyboardKey.KEY_NUMPAD_SUBTRACT,
    0x30: KeyboardKey.KEY_TAB,
    0x0C: KeyboardKey.KEY_Q,
    0x0D: KeyboardKey.KEY_W,
    0x0E: KeyboardKey.KEY_E,
    0x0F: KeyboardKey.KEY_R,
    0x11: KeyboardKey.KEY_T,
    0x10: KeyboardKey.KEY_Y,
    0x20: KeyboardKey.KEY_U,
    0x22: KeyboardKey.KEY_I,
    0x1F: KeyboardKey.KEY_O,
    0x23: KeyboardKey.KEY_P,
    0x21: KeyboardKey.KEY_LEFT_BRACKET,
    0x1E: KeyboardKey.KEY_RIGHT_BRACKET,
    0x2A: KeyboardKey.KEY_BACKSLASH,
    0x75: KeyboardKey.KEY_DELETE,
    0x77: KeyboardKey.KEY_END,
    0x79: KeyboardKey.KEY_PAGE_DOWN,
    0x59: KeyboardKey.KEY_NUMPAD_7,
    0x5B: KeyboardKey.KEY_NUMPAD_8,
    0x5C: KeyboardKey.KEY_NUMPAD_9,
    0x45: KeyboardKey.KEY_NUMPAD_ADD,
    0x39: KeyboardKey.KEY_CAPSLOCK,
    0x00: KeyboardKey.KEY_A,
    0x01: KeyboardKey.KEY_S,
    0x02: KeyboardKey.KEY_D,
    0x03: KeyboardKey.KEY_F,
    0x05: KeyboardKey.KEY_G,
    0x04: KeyboardKey.KEY_H,
    0x26: KeyboardKey.KEY_J,
    0x28: KeyboardKey.KEY_K,
    0x25: KeyboardKey.KEY_L,
    0x29: KeyboardKey.KEY_SEMICOLON,
    0x27: KeyboardKey.KEY_APOSTROPHE,
    0x24: KeyboardKey.KEY_RETURN,
    0x56: KeyboardKey.KEY_NUMPAD_4,
    0x57: KeyboardKey.KEY_NUMPAD_5,
    0x58: KeyboardKey.KEY_NUMPAD_6,
    0x38: KeyboardKey.KEY_LEFT_SHIFT,
    0x06: KeyboardKey.KEY_Z,
    0x07: KeyboardKey.KEY_X,
    0x08: KeyboardKey.KEY_C,
    0x09: KeyboardKey.KEY_V,
    0x0B: KeyboardKey.KEY_B,
    0x2D: KeyboardKey.KEY_N,
    0x2E: KeyboardKey.KEY_M,
    0x2B: KeyboardKey.KEY_COMMA,
    0x2F: KeyboardKey.KEY_PERIOD,
    0x2C: KeyboardKey.KEY_SLASH,
    0x3C: KeyboardKey.KEY_RIGHT_SHIFT,
    0x7E: KeyboardKey.KEY_UP,
    0x53: KeyboardKey.KEY_NUMPAD_1,
    0x54: KeyboardKey.KEY_NUMPAD_2,
    0x55: KeyboardKey.KEY_NUMPAD_3,
    0x4C: KeyboardKey.KEY_NUMPAD_RETURN,
    0x3B: KeyboardKey.KEY_LEFT_CTRL,
    0x3A: KeyboardKey.KEY_LEFT_ALT,
    0x31: KeyboardKey.KEY_SPACE,
    0x3D: KeyboardKey.KEY_RIGHT_ALT,
    0x3E: KeyboardKey.KEY_RIGHT_CTRL,
    0x7B: KeyboardKey.KEY_LEFT,
    0x7D: KeyboardKey.KEY_DOWN,
    0x7C: KeyboardKey.KEY_RIGHT,
    0x52: KeyboardKey.KEY_NUMPAD_0,
    0x41: KeyboardKey.KEY_NUMPAD_PERIOD,
    0x37: KeyboardKey.KEY_LEFT_WINDOWS,
    0x36: KeyboardKey.KEY_RIGHT_WINDOWS,
    0x3f: KeyboardKey.KEY_FN
}

mouse_button_mapping = {
    Quartz.kCGEventLeftMouseDown: MouseButton.LEFT,
    Quartz.kCGEventLeftMouseUp: MouseButton.LEFT,
    Quartz.kCGEventRightMouseDown: MouseButton.RIGHT,
    Quartz.kCGEventRightMouseUp: MouseButton.RIGHT,
    1026: MouseButton.MIDDLE
}