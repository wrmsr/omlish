import os
import threading
import typing as ta

from omlish import lang


##


@ta.final
class _PatchedCacheFile:
    """
    I tried to make a `local_first_pipeline` function to be called instead of `tfm.pipeline`, I really did, but the
    transformers code is such a disgusting rat's nest full of static calls to the caching code strewn about at every
    layer with no concern whatsoever for forwarding kwargs where they need to be.
    """

    def __init__(self, orig: ta.Callable[..., str | None]) -> None:
        self._orig = orig

    def __call__(
            self,
            path_or_repo_id: str | os.PathLike,
            filename: str,
            **kwargs: ta.Any,
    ) -> str | None:
        return self._orig(path_or_repo_id, filename, **kwargs)


_FILE_CACHE_PATCH_LOCK = threading.Lock()


@lang.cached_function(lock=_FILE_CACHE_PATCH_LOCK)
def patch_file_cache() -> None:
    raise NotImplementedError
