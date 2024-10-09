import enum
import typing as ta

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import numpy as np
else:
    np = lang.proxy_import('numpy')


Np: ta.TypeAlias = 'np.ndarray'


##


class Similarity(enum.Enum):
    DOT = enum.auto()
    COSINE = enum.auto()


CalcNpSimilaritiesFunc: ta.TypeAlias = ta.Callable[[Np, Np], Np]

CALC_NP_SIMILARITIES_FUNCS: ta.Mapping[Similarity, CalcNpSimilaritiesFunc] = {}


def register_calc_np_similarities_func(s):
    def inner(fn):
        check.not_in(s, CALC_NP_SIMILARITIES_FUNCS)
        ta.cast(dict, CALC_NP_SIMILARITIES_FUNCS)[s] = fn
        return fn
    return inner


def calc_np_similarities(
        similarity: Similarity,
        haystack: Np,  # (n, d)
        needle: Np,  # (d,)
) -> Np:
    return CALC_NP_SIMILARITIES_FUNCS[similarity](haystack, needle)


##


@register_calc_np_similarities_func(Similarity.DOT)
def calc_np_dot_similarities(
        haystack: Np,  # (n, d)
        needle: Np,  # (d,)
) -> Np:  # (n,)
    return np.dot(haystack, needle)


@register_calc_np_similarities_func(Similarity.COSINE)
def calc_np_cosine_similarities(
        haystack: Np,  # (n, d)
        needle: Np,  # (d,)
) -> Np:  # (n,)
    return np.dot(haystack, needle) / (np.linalg.norm(haystack, axis=1) * np.linalg.norm(needle))
