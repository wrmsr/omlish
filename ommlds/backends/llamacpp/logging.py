"""
FIXME:
 - it outputs newline-terminated so buffer and chop on newlines - DelimitingBuffer again
"""
import ctypes as ct

from omlish import lang


##


@lang.cached_function
def install_logging_hook() -> None:
    import llama_cpp  # noqa
    from llama_cpp import _logger  # noqa

    @llama_cpp.llama_log_callback
    def log_callback(
            level: int,
            text: bytes,
            user_data: ct.c_void_p,
    ) -> None:
        log_level = _logger.GGML_LOG_LEVEL_TO_LOGGING_LEVEL[level] if level != 5 else _logger._last_log_level  # noqa
        if (ts := text.decode('utf-8').rstrip()) != '.' and ts.strip():  # it tends to just output dots lol
            _logger.logger.log(log_level, ts)
        _logger._last_log_level = log_level  # noqa

    llama_cpp.llama_log_set(log_callback, ct.c_void_p(0))  # noqa
