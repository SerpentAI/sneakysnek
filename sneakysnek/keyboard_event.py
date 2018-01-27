import time
import enum


class KeyboardEvents(enum.Enum):
    DOWN = "DOWN"
    UP = "UP"


class KeyboardEvent:

    def __init__(self, event, keyboard_key):
        self.event = event
        self.keyboard_key = keyboard_key
        self.timestamp = time.time()

    def __str__(self):
        return f"KeyboardEvent.{self.event.name} - {self.keyboard_key.name} - {self.timestamp}"
