# ruff: noqa: UP006 UP007 UP037 UP045
# @om-lite
"""
Python equivalents of go standard library functions used by the go-yaml translation, for the cases where python's own
builtins subtly differ from the go semantics the translation must preserve:

 - `str.lstrip` / `str.rstrip` treat their argument as a character set and strip repeatedly, while go's
   `strings.TrimPrefix` / `strings.TrimSuffix` remove one exact affix at most once.
 - `int()` / `float()` are more lenient than go's `strconv` parsers (surrounding whitespace, unicode digits, no 64-bit
   range errors), and `strconv` range errors carry a clamped value that callers like `strconv.Atoi` still use.
 - `str()` formats floats and bools differently than `fmt.Sprint` (`str(True)` vs `'true'`, `str(1.0)` vs `'1'`, and
   go's scientific-notation cutoff of decimal exponent >= 6 or < -4).
 - `chr()` raises on out-of-range code points and passes lone surrogates through, while go's `string(rune(n))`
   substitutes U+FFFD.
 - `base64.b64decode` discards non-alphabet characters and raises on malformed input, while go's
   `base64.StdEncoding.DecodeString` ignores only CR/LF and returns the data decoded before the first error.

All semantics here were verified empirically against go 1.26.
"""
import math
import re
import typing as ta


##
# strings


def yaml_go_trim_prefix(s: str, prefix: str) -> str:
    # strings.TrimPrefix
    if prefix and s.startswith(prefix):
        return s[len(prefix):]
    return s


def yaml_go_trim_suffix(s: str, suffix: str) -> str:
    # strings.TrimSuffix
    if suffix and s.endswith(suffix):
        return s[:len(s) - len(suffix)]
    return s


##
# strconv errors


class YamlGoStrconvError(Exception):
    pass


class YamlGoStrconvSyntaxError(YamlGoStrconvError):  # strconv.ErrSyntax
    pass


class YamlGoStrconvRangeError(YamlGoStrconvError):
    """strconv.ErrRange. Carries the clamped value strconv returns alongside the error."""

    def __init__(self, value: ta.Any) -> None:
        super().__init__(value)

        self.value = value


##
# strconv parsing


def _yaml_go_digit_val(c: str) -> int:
    o = ord(c)
    if 0x30 <= o <= 0x39:
        return o - 0x30
    if 0x61 <= o <= 0x66:
        return o - 0x61 + 10
    if 0x41 <= o <= 0x46:
        return o - 0x41 + 10
    return -1


def _yaml_go_parse_base_digits(s: str, base: int) -> ta.Union[int, YamlGoStrconvError]:
    if not s:
        return YamlGoStrconvSyntaxError()

    n = 0
    for c in s:
        d = _yaml_go_digit_val(c)
        if d < 0 or d >= base:
            return YamlGoStrconvSyntaxError()
        n = n * base + d

    return n


def yaml_go_parse_uint(s: str, base: int, bit_size: int = 64) -> ta.Union[int, YamlGoStrconvError]:
    """strconv.ParseUint with an explicit (non-zero) base: no sign, no underscores, ascii digits only."""

    n = _yaml_go_parse_base_digits(s, base)
    if isinstance(n, YamlGoStrconvError):
        return n

    hi = (1 << bit_size) - 1
    if n > hi:
        return YamlGoStrconvRangeError(hi)

    return n


def yaml_go_parse_int(s: str, base: int, bit_size: int = 64) -> ta.Union[int, YamlGoStrconvError]:
    """strconv.ParseInt with an explicit (non-zero) base: optional sign, no underscores, ascii digits only."""

    if not s:
        return YamlGoStrconvSyntaxError()

    neg = False
    t = s
    if t[0] in ('+', '-'):
        neg = t[0] == '-'
        t = t[1:]

    n = _yaml_go_parse_base_digits(t, base)
    if isinstance(n, YamlGoStrconvError):
        return n

    if neg:
        n = -n

    lo = -(1 << (bit_size - 1))
    hi = (1 << (bit_size - 1)) - 1
    if n < lo:
        return YamlGoStrconvRangeError(lo)
    if n > hi:
        return YamlGoStrconvRangeError(hi)

    return n


def yaml_go_atoi(s: str) -> ta.Union[int, YamlGoStrconvError]:
    # strconv.Atoi
    return yaml_go_parse_int(s, 10, 64)


# Unsigned decimal float syntax per go: underscores permitted only between digits, in the mantissa and the exponent.
_YAML_GO_PARSE_FLOAT_DEC_PAT = r'(?:\d(?:_?\d)*(?:\.(?:\d(?:_?\d)*)?)?|\.\d(?:_?\d)*)(?:[eE][+-]?\d(?:_?\d)*)?'

# Hex float syntax per go: requires the 0x prefix and a mandatory (decimal) p exponent.
_YAML_GO_PARSE_FLOAT_HEX_DIG = r'[0-9a-fA-F]'
_YAML_GO_PARSE_FLOAT_HEX_PAT = (
    r'0[xX]'
    r'(?:H(?:_?H)*(?:\.(?:H(?:_?H)*)?)?|\.H(?:_?H)*)'
    r'[pP][+-]?\d(?:_?\d)*'
).replace('H', _YAML_GO_PARSE_FLOAT_HEX_DIG)

_YAML_GO_PARSE_FLOAT_PAT = re.compile(f'(?:{_YAML_GO_PARSE_FLOAT_DEC_PAT}|{_YAML_GO_PARSE_FLOAT_HEX_PAT})')


def yaml_go_parse_float(s: str) -> ta.Union[float, YamlGoStrconvError]:
    """
    strconv.ParseFloat(s, 64): strict ascii syntax, case-insensitive inf/infinity (signed) and nan (unsigned)
    specials, hex floats with a mandatory p exponent, underscores only between digits. Overflow returns the clamped
    +/-inf via a range error; underflow to zero is not an error (verified against go).
    """

    if not s:
        return YamlGoStrconvSyntaxError()

    if s.lower() == 'nan':
        return math.nan

    neg = False
    t = s
    if t[0] in ('+', '-'):
        neg = t[0] == '-'
        t = t[1:]

    if t.lower() in ('inf', 'infinity'):
        return -math.inf if neg else math.inf

    if _YAML_GO_PARSE_FLOAT_PAT.fullmatch(t) is None:
        return YamlGoStrconvSyntaxError()

    u = ('-' if neg else '') + t.replace('_', '')
    if t[:2].lower() == '0x':
        try:
            v = float.fromhex(u)
        except OverflowError:
            return YamlGoStrconvRangeError(-math.inf if neg else math.inf)
    else:
        v = float(u)

    if math.isinf(v):
        return YamlGoStrconvRangeError(v)

    return v


##
# float formatting


def _yaml_go_split_decimal(r: str) -> ta.Tuple[str, int]:
    """Splits a python fixed or scientific float repr (sans sign) into (significant digits, decimal exponent)."""

    if 'e' in r:
        mant, _, es = r.partition('e')
        exp = int(es)
    else:
        mant, exp = r, 0

    if '.' in mant:
        ip, fp = mant.split('.')
    else:
        ip, fp = mant, ''

    digits = (ip + fp).lstrip('0')
    if not digits:
        return '0', 0

    e = len(ip) - 1 + exp - (len(ip + fp) - len(digits))
    digits = digits.rstrip('0') or '0'
    return digits, e


def yaml_go_format_float(f: float) -> str:
    """
    fmt.Sprint of a float64 - shortest round-trip digits, scientific notation when the decimal exponent is >= 6 or
    < -4, and go's spellings for the specials.
    """

    if math.isnan(f):
        return 'NaN'
    if math.isinf(f):
        return '+Inf' if f > 0 else '-Inf'

    r = repr(f)
    neg = r.startswith('-')
    if neg:
        r = r[1:]

    digits, e = _yaml_go_split_decimal(r)
    sign = '-' if neg else ''

    if e < -4 or e >= 6:
        mant = digits[0] if len(digits) == 1 else f'{digits[0]}.{digits[1:]}'
        return f'{sign}{mant}e{"+" if e >= 0 else "-"}{abs(e):02d}'

    if e >= len(digits) - 1:
        return sign + digits + '0' * (e - (len(digits) - 1))
    if e >= 0:
        return f'{sign}{digits[:e + 1]}.{digits[e + 1:]}'
    return f'{sign}0.{"0" * (-e - 1)}{digits}'


def yaml_go_sprint(v: ta.Any) -> str:
    """fmt.Sprint for the scalar values the decoder can produce."""

    if v is None:
        return '<nil>'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, float):
        return yaml_go_format_float(v)
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    return str(v)


##
# runes


def yaml_go_rune_str(n: int) -> str:
    """string(rune(n)): int32 truncation, with invalid code points and surrogates replaced by U+FFFD."""

    n &= 0xFFFFFFFF
    if n >= 1 << 31:
        n -= 1 << 32
    if n < 0 or n > 0x10FFFF or 0xD800 <= n <= 0xDFFF:
        return '�'
    return chr(n)


##
# base64


_YAML_GO_B64_STD_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

_YAML_GO_B64_STD_ALPHABET_MAP: ta.Mapping[str, int] = {c: i for i, c in enumerate(_YAML_GO_B64_STD_ALPHABET)}


def yaml_go_b64_std_decode(s: str) -> bytes:
    """
    base64.StdEncoding.DecodeString with the error discarded: CR/LF are ignored, and on malformed input the data
    successfully decoded before the error is returned (go returns the partial result alongside the error).
    """

    out = bytearray()
    q: ta.List[int] = []
    pad = 0
    done = False

    for c in s:
        if c in ('\r', '\n'):
            continue
        if done:
            # data after a padding-terminated quantum
            return bytes(out)

        if c == '=':
            if len(q) < 2:
                return bytes(out)
            pad += 1
            q.append(0)
            if len(q) == 4:
                bits = (q[0] << 18) | (q[1] << 12) | (q[2] << 6) | q[3]
                bs = bytes([(bits >> 16) & 0xFF, (bits >> 8) & 0xFF, bits & 0xFF])
                out += bs[:3 - pad]
                done = True
            continue

        if pad:
            # non-padding character inside a padded quantum
            return bytes(out)

        v = _YAML_GO_B64_STD_ALPHABET_MAP.get(c)
        if v is None:
            return bytes(out)

        q.append(v)
        if len(q) == 4:
            bits = (q[0] << 18) | (q[1] << 12) | (q[2] << 6) | q[3]
            out += bytes([(bits >> 16) & 0xFF, (bits >> 8) & 0xFF, bits & 0xFF])
            q = []

    # an unpadded trailing quantum is an error in go's StdEncoding; the full quanta decoded so far are returned
    return bytes(out)
