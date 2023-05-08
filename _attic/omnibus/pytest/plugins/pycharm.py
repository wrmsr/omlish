import threading

from ._registry import register_plugin  # noqa


@register_plugin
class PycharmPlugin:

    def pytest_exception_interact(self, node, call, report):
        try:
            import pydevd
            from pydevd import pydevd_tracing

        except ImportError:
            pass

        else:
            exctype, value, traceback = call.excinfo._excinfo
            frames = []
            while traceback:
                frames.append(traceback.tb_frame)
                traceback = traceback.tb_next

            thread = threading.current_thread()
            frames_by_id = dict([(id(frame), frame) for frame in frames])
            frame = frames[-1]
            exception = (exctype, value, traceback)

            if hasattr(thread, 'additional_info'):
                thread.additional_info.pydev_message = 'test fail'
            try:
                debugger = pydevd.debugger
            except AttributeError:
                debugger = pydevd.get_global_debugger()

            pydevd_tracing.SetTrace(None)
            debugger.stop_on_unhandled_exception(thread, frame, frames_by_id, exception)

        return report
