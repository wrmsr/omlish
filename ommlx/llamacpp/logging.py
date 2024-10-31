"""
FIXME:
 - it outputs newline-terminated so buffer and chop on newlines - DelimitingBuffer again
"""
import ctypes as ct

import llama_cpp
from llama_cpp import _logger as lcl  # noqa

from omlish import lang


##


@llama_cpp.llama_log_callback
def llama_log_callback(
        level: int,
        text: bytes,
        user_data: ct.c_void_p,
) -> None:
    log_level = lcl.GGML_LOG_LEVEL_TO_LOGGING_LEVEL[level] if level != 5 else lcl._last_log_level  # noqa
    if (ts := text.decode('utf-8').rstrip()) != '.' and ts.strip():  # it tends to just output dots lol
        lcl.logger.log(log_level, ts)
    lcl._last_log_level = log_level  # noqa


@lang.cached_function
def install_logging_hook() -> None:
    llama_cpp.llama_log_set(llama_log_callback, ct.c_void_p(0))
