import logging
import typing as ta

from omdev.tui import textual as tx


##


def set_root_logger_to_devtools(devtools: ta.Optional['tx.DevtoolsClient']) -> None:
    from omlish.logs.std.standard import _locking_logging_module_lock  # noqa
    from omlish.logs.std.standard import StandardConfiguredLoggingHandler

    with _locking_logging_module_lock():
        std_handler = next((h for h in logging.root.handlers if isinstance(h, StandardConfiguredLoggingHandler)), None)

        dt_handler = tx.DevtoolsLoggingHandler(devtools, std_handler)

        logging.root.handlers = [dt_handler]
