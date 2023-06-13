import typing as ta


class A:
    def f(self):
        return 'A'

    x = 'A.x'
    y = 'A.y'
    z = 'A.z'


class B(A):
    def f(self):
        return 'B' + super().f()

    x = 'B.x'
    z = 'B.z'


class C(A):
    def f(self):
        return 'C' + super().f()

    y = 'C.y'
    z = 'C.z'


class D(B, C):
    def f(self):
        return 'D' + super().f()

    x = 'D.x'
    y = 'D.y'
    z = 'D.z'


def test_mro():
    assert D().f() == 'DBCA'

    def build_mro_dct(owner_cls: type, instance_cls: type) -> ta.Mapping[str, ta.Any]:
        mro = instance_cls.__mro__[-2::-1]
        try:
            pos = mro.index(owner_cls)
        except ValueError:
            raise TypeError(f'Owner class {owner_cls} not in mro of instance class {instance_cls}')
        dct: ta.Dict[str, ta.Any] = {}
        for cur_cls in mro[:pos + 1]:
            dct.update(cur_cls.__dict__)
        return dct

    print()
    for oc, ic in [
        (D, D),
        (C, D),
        (B, D),
        (A, D),

        (C, C),
        (A, C),

        (B, B),
        (A, B),

        (A, A),
    ]:
        print((oc, ic))
        dct = build_mro_dct(oc, ic)
        print({k: dct[k] for k in dct if not k.startswith('_')})
        print()


def test_descriptor():
    class Desc:
        def __get__(self, instance, owner=None):
            return self

    class A:
        d = Desc()

    class B(A):
        pass

    class C(A):
        pass

    class D(B, C):
        pass

    super()

