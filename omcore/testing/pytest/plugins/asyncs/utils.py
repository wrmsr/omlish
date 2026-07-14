import inspect
import typing as ta


##


def is_coroutine_function(func: ta.Any) -> bool:
    return inspect.iscoroutinefunction(func) or getattr(func, '_is_coroutine', False)


def is_async_function(func: ta.Any) -> bool:
    return is_coroutine_function(func) or inspect.isasyncgenfunction(func)
