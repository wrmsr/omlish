import difflib
import os.path
import typing as ta


##


def get_path_suggestions(
        bad_path: str,
        n: int = 3,
        *,
        filter: ta.Callable[[os.DirEntry], bool] | None = None,  # noqa
        cutoff: float = .6,
) -> ta.Sequence[str] | None:
    dn = os.path.dirname(bad_path)
    try:
        sdi = os.scandir(dn)
    except FileNotFoundError:
        return None

    fl = [
        e.name
        for e in sdi
        if (filter is None or filter(e))
    ]

    return [
        os.path.join(dn, sn)
        for sn in difflib.get_close_matches(
            os.path.basename(bad_path),
            fl,
            n,
            cutoff=cutoff,
        )
    ]
