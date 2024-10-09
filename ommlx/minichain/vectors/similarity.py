import enum
import typing as ta

from omlish import check
from omlish import lang


if ta.TYPE_CHECKING:
    import numpy as np
else:
    np = lang.proxy_import('numpy')


##


class Similarity(enum.Enum):
    DOT = enum.auto()
    COSINE = enum.auto()


Vectorable: ta.TypeAlias = 'np.ndarray'

CalcSimilaritiesFunc: ta.TypeAlias = ta.Callable[[Vectorable, Vectorable], 'np.ndarray']

CALC_SIMILARITIES_FUNCS: ta.Mapping[Similarity, CalcSimilaritiesFunc] = {}


def register_calc_similarities_func(s):
    def inner(fn):
        check.not_in(s, CALC_SIMILARITIES_FUNCS)
        ta.cast(dict, CALC_SIMILARITIES_FUNCS)[s] = fn
        return fn
    return inner


def calc_similarities(
        similarity: Similarity,
        haystack: Vectorable,  # (n, d)
        needle: Vectorable,  # (d,)
) -> 'np.ndarray':
    return CALC_SIMILARITIES_FUNCS[similarity](haystack, needle)


##


@register_calc_similarities_func(Similarity.DOT)
def calc_dot_similarities(
        haystack: Vectorable,  # (n, d)
        needle: Vectorable,  # (d,)
) -> 'np.ndarray':  # (n,)
    return np.dot(haystack, needle)


@register_calc_similarities_func(Similarity.COSINE)
def calc_cosine_similarities(
        haystack: Vectorable,  # (n, d)
        needle: Vectorable,  # (d,)
) -> 'np.ndarray':  # (n,)
    return np.dot(haystack, needle) / (np.linalg.norm(haystack, axis=1) * np.linalg.norm(needle))
