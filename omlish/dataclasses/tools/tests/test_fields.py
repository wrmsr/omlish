import dataclasses as dc

import pytest

from ..fields import install_class_field_attrs


def test_install_class_field_attrs():
    @install_class_field_attrs()
    @dc.dataclass()
    class A:
        x: int
        y: str = 'foo'

    dct = {f.name: f for f in dc.fields(A)}
    assert A.x is dct['x']
    assert A.y is dct['y']

    @install_class_field_attrs()
    @dc.dataclass(frozen=True)
    class B:
        x: int
        y: str = 'foo'

    dct = {f.name: f for f in dc.fields(B)}
    assert B.x is dct['x']
    assert B.y is dct['y']

    with pytest.raises(dc.FrozenInstanceError):
        B(4).y = 'bar'  # type: ignore[misc]  # noqa
