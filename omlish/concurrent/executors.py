import concurrent.futures as cf
import contextlib
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


class ImmediateExecutor(cf.Executor):
    def __init__(self, *, immediate_exceptions: bool = False) -> None:
        super().__init__()
        self._immediate_exceptions = immediate_exceptions

    def submit(
            self,
            fn: ta.Callable[P, T],
            /,
            *args: P.args,
            **kwargs: P.kwargs,
    ) -> cf.Future[T]:
        future: ta.Any = cf.Future()
        try:
            result = fn(*args, **kwargs)
            future.set_result(result)
        except Exception as e:
            if self._immediate_exceptions:
                raise
            future.set_exception(e)
        return future


@contextlib.contextmanager
def new_executor(
        max_workers: int | None = None,
        cls: type[cf.Executor] = cf.ThreadPoolExecutor,
        *,
        immediate_exceptions: bool = False,
        **kwargs: ta.Any,
) -> ta.Generator[cf.Executor, None, None]:
    if max_workers == 0:
        yield ImmediateExecutor(
            immediate_exceptions=immediate_exceptions,
        )

    else:
        with cls(  # type: ignore
                max_workers,
                **kwargs,
        ) as exe:
            yield exe
