import base64
import collections
import re
import typing as ta

from ... import check


def normalize_whitespace(s: str, remove_newline: bool = True) -> str:
    if not s:
        return s
    starts_with_space = (s[0] in ' \n\t\r')
    ends_with_space = (s[-1] in ' \n\t\r')
    if remove_newline:
        newline_re = re.compile('[\r\n]+')
        s = ' '.join(filter(bool, newline_re.split(s)))
    s = ' '.join(filter(bool, s.split('\t')))
    s = ' '.join(filter(bool, s.split(' ')))
    if starts_with_space:
        s = ' ' + s
    if ends_with_space:
        s += ' '
    return s


def levenshtein_distance(s: str, t: str) -> int:
    n = len(s)
    m = len(t)
    if not n:
        return m
    elif not m:
        return n
    d: ta.List[ta.List[int]] = []
    for i in range(n + 1):
        d.append([])
        for j in range(m + 1):
            d[i].append(0)
            d[0][j] = j
        d[i][0] = i
    for i in range(1, n + 1):
        cs = s[i - 1]
        for j in range(1, m + 1):
            ct = t[j - 1]
            cost = 1 if cs != ct else 0
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
    return d[n][m]


class MultipleReplacer:
    """Return a callable that replaces all dict keys by the associated value. More efficient than multiple .replace."""

    # We use an object instead of a lambda function because it avoids the
    # need for using the staticmethod() on the lambda function if assigning
    # it to a class in Python 3.
    def __init__(self, dct) -> None:
        super().__init__()
        self._dict = dct
        dct = dict([(re.escape(key), val) for key, val in dct.items()])
        self._matcher = re.compile('|'.join(dct.keys()))

    def __call__(self, s):
        return self._matcher.sub(lambda m: self._dict[m.group(0)], s)


class MultipleRemover:
    """Return a callable that removes all words in the list. A bit more efficient than MultipleReplacer"""

    # See comment of  MultipleReplacer
    def __init__(self, lst) -> None:
        super().__init__()
        lst = [re.escape(x) for x in lst]
        self._matcher = re.compile('|'.join(lst))

    def __call__(self, s):
        return self._matcher.sub(lambda m: '', s)


def normalize_namreply_params(params: ta.MutableSequence[str]) -> ta.MutableSequence[str]:
    # So… RFC 2812 says:
    #       "( "=" / "*" / "@" ) <channel>
    #       :[ "@" / "+" ] <nick> *( " " [ "@" / "+" ] <nick> )
    # but spaces seem to be missing (eg. before the colon), so we don't know if there should be one before the <channel>
    # and its prefix. So let's normalize this to “with space”, and strip spaces at the end of the nick list.
    if len(params) == 3:
        check.in_(params[1][0], '=*@', params)
        params.insert(1), params[1][0]
        params[2] = params[2][1:]
    params[3] = params[3].rstrip()
    return params


def cap_list_to_dict(l: ta.Iterable[str]) -> ta.Dict[str, str]:
    d = {}
    for cap in l:
        if '=' in cap:
            (key, value) = cap.split('=', 1)
        else:
            key = cap
            value = None
        d[key] = value
    return d


# http://ircv3.net/specs/core/message-tags-3.2.html#escaping-values
TAG_ESCAPE = [
    ('\\', '\\\\'),  # \ -> \\
    (' ', r'\s'),
    (';', r'\:'),
    ('\r', r'\r'),
    ('\n', r'\n'),
]

unescape_tag_value = MultipleReplacer(dict(map(lambda x: (x[1], x[0]), TAG_ESCAPE)))


# TODO: validate host
TAG_KEY_VALIDATOR = re.compile(r'(\S+/)?[a-zA-Z0-9-]+')


def parse_tags(s: str) -> ta.Dict[str, str]:
    tags = {}
    for tag in s.split(';'):
        if '=' not in tag:
            tags[tag] = None
        else:
            (key, value) = tag.split('=', 1)
            check.state(TAG_KEY_VALIDATOR.match(key), 'Invalid tag key: {}'.format(key))
            tags[key] = unescape_tag_value(value)
    return tags


ParsedMessage = collections.namedtuple('ParsedMessage', 'tags prefix command params')


def parse_message(s: str) -> ParsedMessage:
    """
    Parse a message according to
        http://tools.ietf.org/html/rfc1459#section-2.3.1
    and
        http://ircv3.net/specs/core/message-tags-3.2.html
    """

    check.arg(s.endswith('\r\n'), 'Message does not end with CR LF: {!r}'.format(s))
    s = s[0:-2]
    if s.startswith('@'):
        (tags, s) = s.split(' ', 1)
        tags = parse_tags(tags[1:])
    else:
        tags = []
    if ' :' in s:
        (other_tokens, trailing_param) = s.split(' :', 1)
        tokens = list(filter(bool, other_tokens.split(' '))) + [trailing_param]
    else:
        tokens = list(filter(bool, s.split(' ')))
    if tokens[0].startswith(':'):
        prefix = tokens.pop(0)[1:]
    else:
        prefix = None
    command = tokens.pop(0)
    params = tokens
    return ParsedMessage(
        tags=tags,
        prefix=prefix,
        command=command,
        params=params,
    )


def sasl_plain_blob(username: str, passphrase: str) -> str:
    blob = base64.b64encode(
        b'\x00'.join((username.encode('utf-8'), username.encode('utf-8'), passphrase.encode('utf-8'))))
    blobstr = blob.decode('ascii')
    return f'AUTHENTICATE {blobstr}'
