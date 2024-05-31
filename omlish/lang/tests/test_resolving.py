import pytest

from ..resolving import Resolvable
from ..resolving import get_cls_fqcn
from ..resolving import get_fqcn_cls
from ..resolving import ResolvableClassNameError


class Thing(Resolvable):
    # class SubThing(MustBeResolvable):
    #     pass
    pass


def test_resolvable():
    assert get_fqcn_cls(get_cls_fqcn(Thing)) is Thing

    with pytest.raises(ResolvableClassNameError):
        class Bad(Resolvable):  # noqa
            pass
