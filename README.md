# sneakysnek

`sneakysnek` is a minimalistic, cross-platform global input capture solution for Python 3.6+. While there are certainly already offerings in terms of input libraries, they generally focus more on sending input, with capturing only being an afterthought. `sneakysnek` is dead simple in both its design and how you end up using it. You will be up and running in less than 5 lines of code and will start receiving lean & universal events on all 3 supported platforms (Linux, Windows, macOS).

This library was built with the goal of powering the Gameplay Recording feature in the [Serpent.AI Framework](https://github.com/SerpentAI/SerpentAI) where keyboard & mouse inputs are collected alongside frame sequences to build machine learning datasets.

Feel free to study the code to learn more about input capturing and use it responsibly!

![](https://s3.ca-central-1.amazonaws.com/serpent-ai-assets/sneakysnek.gif)

## Installation

```
pip install sneakysnek
```

Zero dependencies on Windows. Will install `pyobjc-framework-Quartz` on macOS and `python-xlib` on Linux.

## Demo

Once installed in your Python environment, you can take it for a quick spin to test it on your platform. Just run `sneakysnek`.

## Usage

Using `sneakysnek` is ridiculously simple:

```python
from sneakysnek.recorder import Recorder

recorder = Recorder.record(print)  # Replace print with any callback that accepts an 'event' arg
# Some blocking code in your main thread...
```

`sneakysnek` runs its capturing and callbacks in separate threads. It should not leave anything behind in most cases. For optimal cleanliness, run `recorder.stop()` from your main thread when you are done recording.

## Events

The callback you provide your recorder with will receive one of the following 2 event objects:

### KeyboardEvent

Represents an event captured from the keyboard.

**Attributes**

* _event_: One of `KeyboardEvents.DOWN`, `KeyboardEvents.UP`
* _keyboard\_key_: One entry from the [KeyboardKey enumeration](https://github.com/SerpentAI/sneakysnek/blob/master/sneakysnek/keyboard_keys.py)
* _timestamp_: A `time.time()` timestamp

### MouseEvent

Represents an event captured from the mouse.

**Attributes**

* _event_: One of `MouseEvents.CLICK`. `MouseEvents.SCROLL`, `MouseEvents.MOVE`
* _button_: One entry from the [MouseButton enumeration](https://github.com/SerpentAI/sneakysnek/blob/master/sneakysnek/mouse_buttons.py)
* _direction_: One of `"DOWN"`, `"UP"`
* _velocity_: An integer representing the velocity of scroll events (only >1 on macOS)
* _x_: An integer representing the x coordinate of the mouse position
* _y_: An integer representing the y coordinate of the mouse position
* _timestamp_: A `time.time()` timestamp

# Enjoying this?

Awesome! For more content, feel free to:

* Learn more about the Serpent.AI Python Framework - [Website](http://serpent.ai) - [Blog](http://blog.serpent.ai) - [Repo](https://github.com/SerpentAI/SerpentAI)
* Watch some Python development on [Twitch](https://www.twitch.tv/serpent_ai) & [YouTube](https://www.youtube.com/c/SerpentAI)
* Follow Serpent.AI on [Twitter](https://twitter.com/Serpent_AI)

### <3