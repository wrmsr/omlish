import pytest

from .. import resolving as rsv_


class Thing(rsv_.Resolvable):
    # class SubThing(MustBeResolvable):
    #     pass
    pass


def test_resolvable():
    assert rsv_.get_fqcn_cls(rsv_.get_cls_fqcn(Thing)) is Thing

    with pytest.raises(rsv_.ResolvableClassNameError):
        class Bad(rsv_.Resolvable):  # noqa
            pass
