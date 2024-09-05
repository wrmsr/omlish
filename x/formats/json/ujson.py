import dataclasses as dc


@dc.dataclass(frozen=True, kw_only=True)
class DumpOpts:
    ensure_ascii
    encode_html_chars
    escape_forward_slashes
    sort_keys
    indent
    allow_nan
    reject_bytes
    default
    separators
