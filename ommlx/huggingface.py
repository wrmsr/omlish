import typing as ta

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import huggingface_hub as hf
    import huggingface_hub.errors  # noqa
    import huggingface_hub.utils  # noqa
else:
    hf = lang.proxy_import('huggingface_hub', extras=[
        'errors',
        'utils',
    ])


def is_repo_cached(
        id: str,  # noqa
        *,
        revisions: ta.Iterable[str] | None = None,
        cache_dir: str | None = None,
) -> bool:
    check.not_isinstance(revisions, str)

    try:
        cache_info = hf.utils.scan_cache_dir(cache_dir=cache_dir)
    except hf.errors.CacheNotFound:
        return False

    revision_set = frozenset(revisions) if revisions is not None else None

    for repo in cache_info.repos:
        if id != repo.repo_id:
            continue

        if revision_set is not None and not any(rev in revision_set for rev in repo.revisions):
            continue

        return True

    return False
