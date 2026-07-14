import re


##


_FLAG_CHARS: tuple[tuple[re.RegexFlag, str], ...] = (
    (re.ASCII, 'a'),
    (re.IGNORECASE, 'i'),
    (re.LOCALE, 'L'),
    (re.MULTILINE, 'm'),
    (re.DOTALL, 's'),
    # intentionally omitting UNICODE ('u')
    (re.VERBOSE, 'x'),
)


def _leading_global_flag_chars(pat: str | bytes) -> set[str]:
    if isinstance(pat, bytes):
        mb = re.match(br'\A\(\?([aiLmsux]+)\)', pat)
        if mb is None:
            return set()
        return set(mb.group(1).decode('ascii'))

    else:
        m = re.match(r'\A\(\?([aiLmsux]+)\)', pat)
        if m is None:
            return set()
        return set(m.group(1))


def regex_to_string(
        pat: str | bytes | re.Pattern[str] | re.Pattern[bytes],
) -> str | bytes:
    if isinstance(pat, (str, bytes)):
        return pat

    flags = pat.flags
    flags &= ~re.DEBUG

    # Unicode is the default for str patterns in Python 3, so don't emit (?u).
    if isinstance(pat.pattern, str):
        flags &= ~re.UNICODE

    existing_flag_chars = _leading_global_flag_chars(pat.pattern)

    flag_str = ''.join(
        ch
        for fl, ch in _FLAG_CHARS
        if flags & fl and ch not in existing_flag_chars
    )

    if not flag_str:
        return pat.pattern

    if isinstance(pat.pattern, bytes):
        return b'(?%b)%b' % (
            flag_str.encode('ascii'),
            pat.pattern,
        )

    return f'(?{flag_str}){pat.pattern}'
