import typing as ta


def swap(f):
    return lambda x, y: f(y, x)


def unzip2(pairs):
    lst1, lst2 = [], []
    for x1, x2 in pairs:
        lst1.append(x1)
        lst2.append(x2)
    return lst1, lst2


def map_(f, *xs):
    return list(map(f, *xs))


def zip_(*args):
    fst, *rest = args = map_(list, args)
    n = len(fst)
    for arg in rest:
        assert len(arg) == n
    return list(zip(*args))


def split_list(lst: ta.List[ta.Any], n: int) -> ta.Tuple[ta.List[ta.Any], ta.List[ta.Any]]:
    assert 0 <= n <= len(lst)
    return lst[:n], lst[n:]


def partition_list(bs: ta.List[bool], l: ta.List[ta.Any]) -> ta.Tuple[ta.List[ta.Any], ta.List[ta.Any]]:
    assert len(bs) == len(l)
    lists = lst1, lst2 = [], []
    for b, x in zip_(bs, l):
        lists[b].append(x)
    return lst1, lst2


class IDHashable:
    val: ta.Any

    def __init__(self, val):
        self.val = val

    def __hash__(self) -> int:
        return id(self.val)

    def __eq__(self, other):
        return type(other) is IDHashable and id(self.val) == id(other.val)


def split_half(lst: ta.List[ta.Any]) -> ta.Tuple[ta.List[ta.Any], ta.List[ta.Any]]:
    assert not len(lst) % 2
    return split_list(lst, len(lst) // 2)


def merge_lists(which: ta.List[bool], l1: ta.List[ta.Any], l2: ta.List[ta.Any]) -> ta.List[ta.Any]:
    l1, l2 = iter(l1), iter(l2)
    out = [next(l2) if b else next(l1) for b in which]
    assert next(l1, None) is next(l2, None) is None
    return out
