import itertools
import typing as ta


T = ta.TypeVar('T')


##


def mut_unify_sets(sets: ta.Iterable[set[T]]) -> list[set[T]]:
    rem: list[set[T]] = list(sets)
    ret: list[set[T]] = []
    while rem:
        cur = rem.pop()
        while True:
            moved = False
            for i in range(len(rem) - 1, -1, -1):
                if any(e in cur for e in rem[i]):
                    cur.update(rem.pop(i))
                    moved = True
            if not moved:
                break
        ret.append(cur)
    if ret:
        all_ = set(itertools.chain.from_iterable(ret))
        num = sum(map(len, ret))
        if len(all_) != num:
            raise ValueError('Length mismatch')
    return ret


def unify_sets(sets: ta.Iterable[ta.AbstractSet[T]]) -> list[set[T]]:
    return mut_unify_sets([set(s) for s in sets])
