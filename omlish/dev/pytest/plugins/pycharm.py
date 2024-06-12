import threading

from ... import pydevd as opd
from ._registry import register


@register
class PycharmPlugin:

    def pytest_addoption(self, parser):
        parser.addoption('--no-pycharm-debug', action='store_true', default=False, help='Disables pycharm debugging')

    def pytest_collection(self, session):
        setup = opd.get_setup()
        if setup is not None:
            if hasattr(session.config, '_env_timeout'):
                session.config._env_timeout = None

    def pytest_exception_interact(self, node, call, report):
        if node.session.config.option.no_pycharm_debug:
            return report

        try:
            import pydevd
            from pydevd import pydevd_tracing
        except ImportError:
            return report

        exctype, value, traceback = call.excinfo._excinfo
        frames = []
        while traceback:
            # FIXME: 3.12 DUPLICATE FRAME IDENTITIES!! prob same shit as greenlet/trio, need to 'pin'
            # FIXME: uhh it happens in 3.11 too and that works lol
            frames.append(traceback.tb_frame)
            traceback = traceback.tb_next

        thread = threading.current_thread()
        frames_by_id = {id(frame): frame for frame in frames}
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
        # debugger.handle_post_mortem_stop(thread, frame, frames_by_id, exception)

        return report
