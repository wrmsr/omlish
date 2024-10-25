"""
loads(obj: str | bytes | bytearray | memoryview) -> ta.Any | oj.JSONDEcodeError
dumps(
    obj: ta.Any,
    default: ta.Callable[[ta.Any], Ata.ny] | None = ...,
    option: int | None = ...,
) -> bytes
"""
import dataclasses as dc
import typing as ta

from .... import lang
from .base import Backend


if ta.TYPE_CHECKING:
    import orjson as oj
else:
    oj = lang.proxy_import('orjson')


##


@dc.dataclass(frozen=True, kw_only=True)
class Options:
    append_newline: bool = False  # append \n to the output

    indent_2: bool = False  # pretty-print output with an indent of two spaces.

    naive_utc: bool = False  # serialize datetime.datetime objects without a tzinfo as UTC

    non_str_keys: bool = False  # serialize dict keys of type other than str

    omit_microseconds: bool = False  # do not serialize the microsecond field on datetime.datetime and datetime.time instances  # noqa

    passthrough_dataclass: bool = False  # passthrough dataclasses.dataclass instances to default
    passthrough_datetime: bool = False  # passthrough datetime.datetime, datetime.date, and datetime.time instances to default  # noqa
    passthrough_subclass: bool = False  # passthrough subclasses of builtin types to default

    serialize_numpy: bool = False  # serialize numpy.ndarray instances

    sort_keys: bool = False  # serialize dict keys in sorted order - the default is to serialize in an unspecified order

    strict_integer: bool = False  # enforce 53-bit limit on integers

    utc_z: bool = False  # serialize a UTC timezone on datetime.datetime instances as Z instead of +00:00

    ##

    def __int__(self) -> int:
        return (
            (oj.OPT_APPEND_NEWLINE if self.append_newline else 0) |

            (oj.OPT_INDENT_2 if self.indent_2 else 0) |

            (oj.OPT_NAIVE_UTC if self.naive_utc else 0) |

            (oj.OPT_NON_STR_KEYS if self.non_str_keys else 0) |

            (oj.OPT_OMIT_MICROSECONDS if self.omit_microseconds else 0) |

            (oj.OPT_PASSTHROUGH_DATACLASS if self.passthrough_dataclass else 0) |
            (oj.OPT_PASSTHROUGH_DATETIME if self.passthrough_datetime else 0) |
            (oj.OPT_PASSTHROUGH_SUBCLASS if self.passthrough_subclass else 0) |

            (oj.OPT_SERIALIZE_NUMPY if self.serialize_numpy else 0) |

            (oj.OPT_SORT_KEYS if self.sort_keys else 0) |

            (oj.OPT_STRICT_INTEGER if self.strict_integer else 0) |

            (oj.OPT_UTC_Z if self.utc_z else 0)
        )


@dc.dataclass(frozen=True, kw_only=True)
class DumpOpts:
    default: ta.Callable[[ta.Any], ta.Any] | None = None
    option: Options = Options()


##


class OrjsonBackend(Backend):
    def dump(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        fp.write(self.dumps(obj, **kwargs))

    def dumps(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return oj.dumps(obj, **kwargs).decode('utf-8')

    def load(self, fp: ta.Any, **kwargs: ta.Any) -> ta.Any:
        return oj.loads(fp.read(), **kwargs)

    def loads(self, s: str | bytes | bytearray, **kwargs: ta.Any) -> ta.Any:
        return oj.loads(s, **kwargs)

    def dump_pretty(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        fp.write(self.dumps_pretty(obj, **kwargs))

    def dumps_pretty(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return self.dumps(obj, option=kwargs.pop('option', 0) | oj.OPT_INDENT_2, **kwargs)

    def dump_compact(self, obj: ta.Any, fp: ta.Any, **kwargs: ta.Any) -> None:
        return self.dump(obj, fp, **kwargs)

    def dumps_compact(self, obj: ta.Any, **kwargs: ta.Any) -> str:
        return self.dumps(obj, **kwargs)


ORJSON_BACKEND: OrjsonBackend | None
if lang.can_import('orjson'):
    ORJSON_BACKEND = OrjsonBackend()
else:
    ORJSON_BACKEND = None
