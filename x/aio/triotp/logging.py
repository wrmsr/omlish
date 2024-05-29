"""
TriOTP logging system relies on the Logbook_ library. Each node has its own log
handler.

.. _logbook: https://logbook.readthedocs.io/
"""

from enum import Enum, auto
import logging


class LogLevel(Enum):
    """
    TriOTP node's logging level
    """

    NONE = auto()  #: Logging is disabled
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

    def to_logbook(self) -> int:
        """
        Convert this enum to a Logbook log level.

        :returns: Logbook log level
        """

        return logging.getLevelNamesMapping[self.name]


def getLogger(name: str) -> logging.Logger:
    """
    Get a logger by name.

    :param name: Name of the logger
    :returns: Logbook Logger instance
    """

    return logging.getLogger(name)
