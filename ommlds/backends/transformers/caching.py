import os
import threading
import typing as ta

from omlish import lang

from ..._hacks.funcs import create_detour


##


_FILE_CACHE_PATCH_LOCK = threading.Lock()


@lang.cached_function(lock=_FILE_CACHE_PATCH_LOCK)
def patch_file_cache() -> None:
    """
    I tried to make a `local_first_pipeline` function to be called instead of `tfm.pipeline`, I really did, but the
    transformers code is such a disgusting rat's nest full of direct static calls to the caching code strewn about at
    every layer with no concern whatsoever for forwarding kwargs where they need to go.
    """

    from transformers.utils.hub import cached_files

    orig_cached_files: ta.Callable[..., str | None] = lang.copy_function(cached_files)  # type: ignore

    def new_cached_files(
            path_or_repo_id: str | os.PathLike,
            filenames: list[str],
            **kwargs: ta.Any,
    ) -> str | None:
        return orig_cached_files(path_or_repo_id, filenames, **kwargs)

    cached_files.__code__ = create_detour(cached_files, new_cached_files, as_kwargs=True)
