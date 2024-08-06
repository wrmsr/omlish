import logging
import sys

from omlish.diag import pydevd as pdu


log = logging.getLogger(__name__)


def handle_error_debug(e: BaseException) -> None:
    exc_info = sys.exc_info()
    log.warning('Launching debugger')
    pdu.debug_unhandled_exception(exc_info)
    log.warning('Done debugging')
