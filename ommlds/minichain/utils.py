import typing as ta

from omlish import check
from omlish import reflect as rfl


##


def join_human_readable_str_list(
        strs: ta.Iterable[str],
        *,
        sep: str = ', ',
        disj: str = 'or ',
) -> str:
    seq = list(strs)
    return sep.join(
        (disj if i == len(seq) - 1 else '') + s
        for i, s in enumerate(seq)
    )


##


def str_literal_values(lit: ta.Any) -> ta.Sequence[str]:
    return tuple(check.isinstance(rfl.type_(lit), rfl.Literal).args)
