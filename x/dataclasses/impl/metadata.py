import types
import typing as ta


METADATA_ATTR = '__dataclass_metadata__'

Metadata: ta.TypeAlias = ta.Mapping[ta.Any, ta.Any]

EMPTY_METADATA = types.MappingProxyType({})
