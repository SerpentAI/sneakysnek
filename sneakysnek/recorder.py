import sys


class RecorderError(BaseException):
    pass


class Recorder:

    def __init__(self, callback):
        self.backend = self._initialize_backend()

        self.callback = callback
        self.is_recording = False

    def start(self, callback):
        pass

    def _initialize_backend(self):
        if sys.platform in ["linux", "linux2"]:
            import sneakysnek.recorders.linux_recorder
            self.backend = sneakysnek.recorders.linux_recorder.LinuxRecorder()
        elif sys.platform == "darwin":
            import sneakysnek.recorders.mac_os_recorder
            self.backend = sneakysnek.recorders.mac_os_recorder.MacOSRecorder()
        elif sys.platform == "win32":
            import sneakysnek.recorders.windows_recorder
            self.backend = sneakysnek.recorders.windows_recorder.WindowsRecorder()
        else:
            raise RecorderError(f"Unsupported platform '{sys.platform}'")