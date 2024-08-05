import logging
import sys
import threading


log = logging.getLogger(__name__)


def handle_error_debug(e: BaseException) -> None:
    exc_info = sys.exc_info()

    try:
        import pydevd
        from pydevd import pydevd_tracing

    except ImportError:
        return

    exctype, value, traceback = exc_info
    frames = []
    while traceback:
        frames.append(traceback.tb_frame)
        traceback = traceback.tb_next

    thread = threading.current_thread()
    frames_by_id = {id(frame): frame for frame in frames}
    frame = frames[-1]
    exception = (exctype, value, traceback)

    if hasattr(thread, 'additional_info'):
        thread.additional_info.pydev_message = 'server exception'
    try:
        debugger = pydevd.debugger
    except AttributeError:
        debugger = pydevd.get_global_debugger()

    pydevd_tracing.SetTrace(None)

    log.warning('Launching debugger')
    debugger.stop_on_unhandled_exception(thread, frame, frames_by_id, exception)
    log.warning('Done debugging')
