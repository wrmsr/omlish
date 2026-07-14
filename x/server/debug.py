import sys

from omcore.diag import pydevd as pdu
from omcore.logs import all as logs


log = logs.get_module_logger(globals())


##


def handle_error_debug(e: BaseException) -> None:
    exc_info = sys.exc_info()
    log.warning('Launching debugger')
    pdu.debug_unhandled_exception(exc_info)
    log.warning('Done debugging')
