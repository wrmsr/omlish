import dataclasses as dc


@dc.dataclass(frozen=True, kw_only=True)
class DumpOpts:
    skipkeys = False
    ensure_ascii = True
    check_circular = True
    allow_nan = True
    cls = None
    indent = None
    separators = None
    default = None
    sort_keys = False
