import dataclasses as _dc

from .impl import dataclass as _dataclass
from .impl import field as _field


##

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


from dataclasses import dataclass  # noqa


globals()['dataclass'] = _dataclass

field = _field
