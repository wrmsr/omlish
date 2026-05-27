"""
Link-component scanners: label, destination, title.

These cover the syntactic pieces needed to parse reference link definitions and inline links. We keep them single-line
at this scanner level; multi-line orchestration (refdefs can span up to 3 lines per CommonMark §4.7) lives in the parser
that uses these.
"""
from omlish import dataclasses as dc

from .whitespace import is_ascii_punctuation


##


_MAX_LABEL_CODEPOINTS = 1000  # CommonMark cap


@dc.dataclass(frozen=True)
class LinkLabelScan:
    end: int  # index in text just past the closing `]`
    raw: str  # label content as it appeared (between brackets), unnormalized


# pulldown-cmark/src/linklabel.rs::scan_link_label_rest - single-line version. We do NOT do whitespace collapsing here;
# the caller normalizes via `normalize_link_label`.
def scan_link_label(text: str, start: int) -> LinkLabelScan | None:
    """
    Scan a `[label]` starting at `text[start]` (which must be `[`). Returns the parse result, or None if the label is
    malformed or empty after normalization.

    Disallows nested `[` and unescaped `]`. Backslash escapes of ASCII punctuation are honored. Returns None if the
    label contains only whitespace (CommonMark requires non-whitespace content).
    """

    n = len(text)
    if start >= n or text[start] != '[':
        return None
    i = start + 1
    cps = 0
    only_ws = True
    while i < n:
        if cps > _MAX_LABEL_CODEPOINTS:
            return None
        c = text[i]
        if c == '[':
            return None
        if c == ']':
            if only_ws:
                return None
            return LinkLabelScan(end=i + 1, raw=text[start + 1:i])
        if c == '\\' and i + 1 < n and is_ascii_punctuation(text[i + 1]):
            i += 2
            cps += 2
            only_ws = False
            continue
        if c not in ' \t':
            only_ws = False
        i += 1
        cps += 1
    return None  # ran off the end without closing


def normalize_link_label(raw: str) -> str:
    """
    Per CommonMark §4.7: trim leading / trailing whitespace, collapse any run of internal whitespace (including line
    breaks) to a single space, and Unicode-casefold.
    """

    return ' '.join(raw.split()).casefold()


@dc.dataclass(frozen=True)
class LinkDestScan:
    end: int   # index in text just past the destination
    dest: str  # the destination (angle brackets stripped if present; escapes preserved)


# pulldown-cmark/src/scanners.rs::scan_link_dest - restricted to single-line use here.
def scan_link_destination(text: str, start: int, *, max_parens: int = 32) -> LinkDestScan | None:
    n = len(text)
    if start >= n:
        return None

    if text[start] == '<':
        # Angle-bracketed form: any chars but unescaped `<`, `\n`, or `\r`; ends at `>`.
        i = start + 1
        out: list[str] = []
        while i < n:
            c = text[i]
            if c == '>':
                return LinkDestScan(end=i + 1, dest=''.join(out))
            if c == '\n' or c == '\r' or c == '<':
                return None
            if c == '\\' and i + 1 < n and is_ascii_punctuation(text[i + 1]):
                out.append(text[i + 1])
                i += 2
                continue
            out.append(c)
            i += 1
        return None

    # Bare form: balanced parens; terminates at first ASCII control / space / unbalanced ')'.
    i = start
    depth = 0
    out = []
    while i < n:
        c = text[i]
        if ord(c) < 0x20 or c == ' ':
            break
        if c == '\\' and i + 1 < n and is_ascii_punctuation(text[i + 1]):
            out.append(text[i + 1])
            i += 2
            continue
        if c == '(':
            depth += 1
            if depth > max_parens:
                return None
        elif c == ')':
            if depth == 0:
                break
            depth -= 1
        out.append(c)
        i += 1

    if i == start:
        return None
    if depth != 0:
        return None

    return LinkDestScan(end=i, dest=''.join(out))


@dc.dataclass(frozen=True)
class LinkTitleScan:
    end: int    # index in text just past the title's closing delimiter
    title: str  # title content (delimiters stripped; escapes preserved)


# pulldown-cmark/src/scanners.rs scans titles inline; we factor it out. Single-line for now.
def scan_link_title(text: str, start: int) -> LinkTitleScan | None:
    n = len(text)
    if start >= n:
        return None
    open_ = text[start]
    if open_ == '"':
        close = '"'
    elif open_ == "'":
        close = "'"
    elif open_ == '(':
        close = ')'
    else:
        return None
    i = start + 1
    out: list[str] = []
    while i < n:
        c = text[i]
        if c == close:
            return LinkTitleScan(end=i + 1, title=''.join(out))
        if open_ == '(' and c == '(':
            return None  # `(...)` titles disallow nested unescaped `(`
        if c == '\\' and i + 1 < n and is_ascii_punctuation(text[i + 1]):
            out.append(text[i + 1])
            i += 2
            continue
        out.append(c)
        i += 1
    return None
