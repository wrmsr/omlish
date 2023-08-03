import collections.abc
import itertools

from .. import c3


def test_mro():
    class A:
        pass

    class B(A):
        pass

    class C(A):
        pass

    class D(B, C):
        pass

    assert c3.mro(D, []) == [D, B, C, A, object]

    c = collections.abc

    bases: list[type] = [c.Sequence, c.MutableMapping, c.Mapping, c.Set]
    for haystack in itertools.permutations(bases):
        m = c3.compose_mro(dict, haystack)
        assert m == [
            dict,
            c.MutableMapping,
            c.Mapping,
            c.Collection,
            c.Sized,
            c.Iterable,
            c.Container,
            object,
        ]

    bases = [c.Container, c.Mapping, c.MutableMapping, collections.OrderedDict]
    for haystack in itertools.permutations(bases):
        m = c3.compose_mro(collections.ChainMap, haystack)
        assert m == [
            collections.ChainMap,
            c.MutableMapping,
            c.Mapping,
            c.Collection,
            c.Sized,
            c.Iterable,
            c.Container,
            object,
        ]
