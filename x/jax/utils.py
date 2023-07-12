import builtins
import typing as ta


def swap(f):
    return lambda x, y: f(y, x)


def unzip2(pairs):
    lst1, lst2 = [], []
    for x1, x2 in pairs:
        lst1.append(x1)
        lst2.append(x2)
    return lst1, lst2


def map(f, *xs):
    return list(builtins.map(f, *xs))


def zip(*args):
    fst, *rest = args = map(list, args)
    n = len(fst)
    for arg in rest:
        assert len(arg) == n
    return list(builtins.zip(*args))


def split_list(lst: ta.List[ta.Any], n: int) -> ta.Tuple[ta.List[ta.Any], ta.List[ta.Any]]:
    assert 0 <= n <= len(lst)
    return lst[:n], lst[n:]


def partition_list(bs: ta.List[bool], l: ta.List[ta.Any]) -> ta.Tuple[ta.List[ta.Any], ta.List[ta.Any]]:
    assert len(bs) == len(l)
    lists = lst1, lst2 = [], []
    for b, x in zip(bs, l):
        lists[b].append(x)
    return lst1, lst2
