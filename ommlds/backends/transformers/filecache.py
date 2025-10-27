import contextlib
import dataclasses as dc
import os
import threading
import typing as ta

import transformers as tfm

from omlish import lang

from ..._hacks.funcs import create_detour


##


@dc.dataclass(frozen=True, kw_only=True)
class _FileCachePatchContext:
    local_first: bool = False
    local_config_present_is_authoritative: bool = False


_FILE_CACHE_PATCH_CONTEXT_TLS = threading.local()


def _get_file_cache_patch_context() -> _FileCachePatchContext:
    try:
        return _FILE_CACHE_PATCH_CONTEXT_TLS.context
    except AttributeError:
        ctx = _FILE_CACHE_PATCH_CONTEXT_TLS.context = _FileCachePatchContext()
        return ctx


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

    get_file_cache_patch_context = _get_file_cache_patch_context

    def new_cached_files(
            path_or_repo_id: str | os.PathLike,
            filenames: list[str],
            **kwargs: ta.Any,
    ) -> str | None:
        ctx = get_file_cache_patch_context()

        if ctx.local_first and not kwargs.get('local_files_only'):
            try:
                local = orig_cached_files(
                    path_or_repo_id,
                    filenames,
                    **{**kwargs, 'local_files_only': True},
                )
            except OSError as e:  # noqa
                pass
            else:
                return local

            if ctx.local_config_present_is_authoritative:
                try:
                    local_config = orig_cached_files(
                        path_or_repo_id,
                        [tfm.CONFIG_NAME],
                        **{**kwargs, 'local_files_only': True},
                    )
                except OSError as e:  # noqa
                    pass
                else:
                    raise OSError(
                        f'Files {filenames!r} requested under local_first '
                        f'but local_config present at {local_config!r}, '
                        f'assuming files do not exist.',
                    )

        return orig_cached_files(path_or_repo_id, filenames, **kwargs)

    cached_files.__code__ = create_detour(cached_files, new_cached_files, as_kwargs=True)


@contextlib.contextmanager
def file_cache_patch_context(
        *,
        local_first: bool = False,
        local_config_present_is_authoritative: bool = False,
) -> ta.Generator[None]:
    patch_file_cache()

    new_ctx = dc.replace(
        old_ctx := _get_file_cache_patch_context(),
        local_first=local_first,
        local_config_present_is_authoritative=local_config_present_is_authoritative,
    )

    _FILE_CACHE_PATCH_CONTEXT_TLS.context = new_ctx
    try:
        yield
    finally:
        _FILE_CACHE_PATCH_CONTEXT_TLS.context = old_ctx
