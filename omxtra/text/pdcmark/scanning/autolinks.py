"""
Autolink scanners.

CommonMark §6.5: an autolink is `<` followed by either an absolute URI or an email address, followed by `>`. The
autolink renders as a link with the URI as its destination.

URI autolink rules:
  - scheme: 2-32 chars, starts with ASCII letter, contains [A-Za-z0-9+-.]
  - followed by `:`
  - body: any char other than ASCII control chars, space, `<`, or `>`
Email autolink:
  - local@domain, matches a specific regex from the CommonMark spec.
"""
import re

from omlish import dataclasses as dc


##


_RE_URI = re.compile(
    r'[A-Za-z][A-Za-z0-9+.\-]{1,31}:[^\s<>\x00-\x1f]*',
)


# Per CM §6.5 — direct port of the spec regex.
_RE_EMAIL = re.compile(
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",
)


@dc.dataclass(frozen=True)
class AutolinkMatch:
    end: int      # one past the closing `>`
    target: str   # raw URI / email (no `mailto:` prefix here)
    is_email: bool


# pulldown-cmark/src/scanners.rs::scan_autolink
def scan_autolink(text: str, start: int) -> AutolinkMatch | None:
    if start >= len(text) or text[start] != '<':
        return None
    # Find the `>`.
    close = text.find('>', start + 1)
    if close < 0:
        return None
    body = text[start + 1:close]
    if not body:
        return None
    # Reject if body contains whitespace.
    if any(c.isspace() or c == '<' for c in body):
        return None
    # Try URI form first (must contain `:` after scheme).
    if _RE_URI.fullmatch(body):
        return AutolinkMatch(end=close + 1, target=body, is_email=False)
    if _RE_EMAIL.fullmatch(body):
        return AutolinkMatch(end=close + 1, target=body, is_email=True)
    return None
