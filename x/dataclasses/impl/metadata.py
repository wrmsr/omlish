import types
import typing as ta


METADATA_ATTR = '__dataclass_metadata__'

Metadata: ta.TypeAlias = ta.Mapping[ta.Any, ta.Any]

EMPTY_METADATA = types.MappingProxyType({})


def get_metadata(cls: type) -> Metadata:
    if not isinstance(cls, type):
        raise TypeError(cls)
    return cls.__dict__.get(METADATA_ATTR, EMPTY_METADATA)
