from .. import annotations as an
from ...serde import mapping as sm


class TestAnn(an.Annotation, abstract=True):
    pass


class TestAnns(an.Annotations[TestAnn]):
    pass


class A(TestAnn):
    pass


class B(TestAnn):
    v: int


def test_annotations():
    anns = TestAnns()
    s = sm.serialize(anns)
    assert s == {}
    d = sm.deserialize(s, TestAnns)
    assert anns == d

    anns = TestAnns([A(), B(1)])
    assert anns[B].v == 1

    s = sm.serialize(anns)
    d = sm.deserialize(s, TestAnns)
    assert anns == d

    anns = TestAnns({**{A: A(), B: B(1)}, B: B(2)})
    assert anns[B].v == 2

    anns2 = TestAnns({**anns, B: B(3)})
    assert anns[A] is anns2[A]
    assert anns2[B].v == 3

    anns2 = TestAnns(anns)
    assert anns == anns2
