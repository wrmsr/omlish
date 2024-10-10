"""
def loads(obj: str | bytes | bytearray | memoryview) -> ta.Any | oj.JSONDEcodeError
def dumps(obj: ta.Any, **DumpOpts) -> bytes
"""
import dataclasses as dc
import typing as ta

from .... import lang


if ta.TYPE_CHECKING:
    import orjson as oj
else:
    oj = lang.proxy_import('orjson')


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
