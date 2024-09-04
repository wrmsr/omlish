class Backend:
    pass


class JsonBackend(Backend):
    """
    dump
      skipkeys=False
      ensure_ascii=True
      check_circular=True
      allow_nan=True
      cls=None
      indent=None
      separators=None
      default=None
      sort_keys=False
    dumps
      ^
    load
      cls=None
      object_hook=None
      parse_float=None
      parse_int=None
      parse_constant=None
      object_pairs_hook=None
    loads
      ^
    """


class UjsonBackend(Backend):
    """
    dump
      ensure_ascii
      encode_html_chars
      escape_forward_slashes
      sort_keys
      indent
      allow_nan
      reject_bytes
      default
      separators
    dumps
      ^
    load
    loads
    """


class OrjsonBackend(Backend):
    """
    dumps
      default
      option
        OPT_INDENT_2
        OPT_NAIVE_UTC
        OPT_NON_STR_KEYS
        OPT_OMIT_MICROSECONDS
        OPT_PASSTHROUGH_DATACLASS
        OPT_PASSTHROUGH_DATETIME
        OPT_PASSTHROUGH_SUBCLASS
        OPT_SERIALIZE_DATACLASS
        OPT_SERIALIZE_NUMPY
        OPT_SERIALIZE_UUID
        OPT_SORT_KEYS
        OPT_STRICT_INTEGER
        OPT_UTC_Z
    loads
    """


class RapidjsonBackend(Backend):
    """
    dump
      skipkeys=False,
      ensure_ascii=True,
      write_mode=WM_COMPACT,
        WM_COMPACT
        WM_PRETTY
        WM_SINGLE_LINE_ARRAY
      indent=4,
      default=None,
      sort_keys=False,
      number_mode=None,
        NM_NONE
        NM_DECIMAL
        NM_NAN
        NM_NATIVE
      datetime_mode=None,
        DM_NONE
        DM_ISO8601
        DM_UNIX_TIME
        DM_ONLY_SECONDS
        DM_IGNORE_TZ
        DM_NAIVE_IS_UTC
        DM_SHIFT_TO_UTC
      uuid_mode=None,
        UM_NONE
        UM_CANONICAL
        UM_HEX
      bytes_mode=BM_UTF8,
        BM_NONE
        BM_UTF8
      iterable_mode=IM_ANY_ITERABLE,
        IM_ANY_ITERABLE
        IM_ONLY_LISTS
      mapping_mode=MM_ANY_MAPPING,
        MM_ANY_MAPPING
        MM_ONLY_DICTS
        MM_COERCE_KEYS_TO_STRINGS
        MM_SKIP_NON_STRING_KEYS
        MM_SORT_KEYS
      chunk_size
      allow_nan=True
    dumps
      ^
      -chunk_size
    load
      object_hook=None,
      number_mode=None,
        ^
      datetime_mode=None,
        ^
      uuid_mode=None,
        ^
      parse_mode=None,
        PM_NONE
        PM_COMMENTS
        PM_TRAILING_COMMAS
      chunk_size=65536,
      allow_nan=True
    loads
      ^
      -chunk_size
    """
