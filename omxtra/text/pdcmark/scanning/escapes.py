"""
Backslash escape recognition.

CommonMark §6.1: any ASCII punctuation character may be backslash-escaped. The backslash is suppressed and the
punctuation character is rendered as-is. Backslash escapes are NOT recognized inside code spans, autolinks, or raw HTML.
"""
from .whitespace import is_ascii_punctuation


##


# pulldown-cmark uses an ItemBody::Text {backslash_escaped: true} flag plus is_ascii_punctuation in scanners.rs; the
# recognition itself is just "is this char ASCII punct".
def is_escapable(c: str) -> bool:
    return is_ascii_punctuation(c)
