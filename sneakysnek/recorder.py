import sys


class RecorderError(BaseException):
    pass


class Recorder:

    def __init__(self, callback):
        self.backend = None

        self._initialize_backend(callback)

    def _initialize_backend(self, callback):
        if sys.platform in ["linux", "linux2"]:
            import sneakysnek.recorders.linux_recorder
            self.backend = sneakysnek.recorders.linux_recorder.LinuxRecorder(callback)
        elif sys.platform == "darwin":
            import sneakysnek.recorders.mac_os_recorder
            self.backend = sneakysnek.recorders.mac_os_recorder.MacOSRecorder(callback)
        elif sys.platform == "win32":
            import sneakysnek.recorders.windows_recorder
            self.backend = sneakysnek.recorders.windows_recorder.WindowsRecorder(callback)
        else:
            raise RecorderError(f"Unsupported platform '{sys.platform}'")

    @classmethod
    def record(cls, callback):
        recorder = cls(callback)
        recorder.backend.__class__.record(callback)
