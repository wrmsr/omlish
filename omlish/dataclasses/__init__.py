import dataclasses as _dc


Field = _dc.Field
FrozenInstanceError = _dc.FrozenInstanceError
InitVar = _dc.InitVar
MISSING = _dc.MISSING

fields = _dc.fields
asdict = _dc.asdict
astuple = _dc.astuple
make_dataclass = _dc.make_dataclass
replace = _dc.replace
is_dataclass = _dc.is_dataclass

##


from .impl import dataclass as _dataclass  # noqa
from .impl import field as _field  # noqa
from .mcls import Data  # noqa
from .mcls import DataMeta  # noqa
from .md import KwOnly  # noqa
from .md import check  # noqa
from .md import init  # noqa
from .md import metadata  # noqa
from .md import tag  # noqa

##


from dataclasses import dataclass  # noqa


globals()['dataclass'] = _dataclass

field = _field
