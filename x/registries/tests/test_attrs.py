import typing as ta

from ..attrs import RegistryClassAttr


def test_attrs():
    class C0:
        rca: ta.ClassVar[RegistryClassAttr[str, ta.Any]] = RegistryClassAttr()

        @rca.register('k1')
        def m1_0(self):
            pass

        @rca.register('k1')
        def m1_1(self):
            pass

        @rca.register('k2')
        def m2(self):
            pass

    class C1(C0):
        @C0.rca.register('k1')
        def m1_2(self):
            pass

        def m1_1(self):
            pass

    print(C0.rca._get_cls_attrs(C0))
    print(C0.rca._get_cls_attrs(C1))
    print(C0.rca._get_cls_attrs(C1, C0))
