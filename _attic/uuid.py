import typing as ta
import uuid


try:
    import fastuuid

except ImportError:
    uuid3 = uuid.uuid3
    uuid4 = uuid.uuid4
    uuid5 = uuid.uuid5

    def uuid4_bulk(n: int) -> ta.List[uuid.UUID]:
        return [uuid4() for _ in range(n)]

    def uuid4_as_strings_bulk(n: int) -> ta.List[str]:
        return [str(uuid4()) for _ in range(n)]

else:
    uuid3 = fastuuid.uuid3
    uuid4 = fastuuid.uuid4
    uuid5 = fastuuid.uuid5
    uuid4_bulk = fastuuid.uuid4_bulk
    uuid4_as_strings_bulk = fastuuid.uuid4_as_strings_bulk


def new(
        hex=None,
        bytes=None,
        bytes_le=None,
        fields=None,
        int=None,
        version=None,
        *,
        is_safe=uuid.SafeUUID.unknown,
) -> uuid.UUID:
    return uuid.UUID(
        hex,
        bytes,
        bytes_le,
        fields,
        int,
        version,
        is_safe=is_safe
    )


try:
    from ._ext.cy import uuid as _uuid  # type: ignore
except ImportError:
    globals()['new'] = uuid.UUID
else:
    globals()['new'] = _uuid.make


UUID = uuid.UUID
ZERO = uuid.UUID('00000000-0000-0000-0000-000000000000')


DASH_SLICES = [
    slice(0, 8),
    slice(8, 12),
    slice(12, 16),
    slice(16, 20),
    slice(20, 32),
]


def int_to_uuid_str(i: int) -> str:
    s = '%032x' % (i,)
    return '-'.join(s[sl] for sl in DASH_SLICES)


def int_to_uuid(i: int) -> uuid.UUID:
    return uuid.UUID(int_to_uuid_str(i))


def uuid_to_int(u: ta.Union[uuid.UUID, str]) -> int:
    return int(str(u).replace('-', ''), 16)
