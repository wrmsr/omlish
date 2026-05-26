"""
Exception hierarchy.

Kept small for now. Concrete subclasses will be added as the parser grows actual failure modes.
"""


##


class PdcmarkError(Exception):
    pass


class ParserStateError(PdcmarkError):
    """Raised when the parser is used incorrectly — e.g. `feed()` after `finish()`."""


class ResourceLimitExceededError(PdcmarkError):
    """
    Raised when a DoS-mitigation limit (nesting depth, fuel, …) is exceeded.

    See `pulldown-cmark/src/parse.rs::LINK_MAX_NESTED_PARENS` and `ParserInner::link_ref_expansion_limit` for the
    analogous Rust-side guards.
    """
