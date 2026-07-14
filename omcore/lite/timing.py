from ..logs.modules import get_module_logger
from ..logs.utils import LogTimingContext
from ..logs.utils import log_timing_context


log = get_module_logger(globals())  # noqa


LogTimingContext.DEFAULT_LOG = log

log_timing_context = log_timing_context  # noqa
