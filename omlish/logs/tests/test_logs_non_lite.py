import logging

from ... import lang
from ..base import NopLogger
from ..protocols import LoggerLike


lang.static_check_issubclass[LoggerLike](NopLogger)
lang.static_check_issubclass[LoggerLike](logging.Logger)
