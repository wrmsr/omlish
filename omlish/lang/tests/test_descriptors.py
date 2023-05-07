from ..descriptors import access_forbidden
from ..descriptors import AccessForbiddenException


def test_access_forbidden():
    class C:
        f = access_forbidden()

    try:
        C.f
    except AccessForbiddenException as e:
        assert e.name == 'f'
