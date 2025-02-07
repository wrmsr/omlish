from ..logs.timing import LogTimingContext
from ..logs.timing import log_timing_context
from .logs import log


LogTimingContext.DEFAULT_LOG = log

log_timing_context = log_timing_context  # noqa
