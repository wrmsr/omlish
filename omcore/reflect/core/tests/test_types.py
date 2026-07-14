from ..symbols import TypeInfo
from ..types import Instance
from ..types import NoneType
from ..types import UnionType
from .helpers import make_info


def test_match_args():
    int_or_none = UnionType((Instance(make_info('builtins.int')), NoneType()))

    match int_or_none:
        case UnionType((
            Instance(TypeInfo('builtins.int')),
            NoneType(),
        )):
            pass
        case _:
            raise ValueError('did not match')
