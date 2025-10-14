from .errors import InvalidTagContentError


##


# Mapping for escaping tag values
TAG_VAL_TO_ESCAPE = {
    '\\': '\\\\',
    ';': '\\:',
    ' ': '\\s',
    '\r': '\\r',
    '\n': '\\n',
}


TAG_ESCAPE_CHAR_LOOKUP_TABLE = {i: chr(i) for i in range(256)}  # Most chars escape to themselves

# These are the exceptions
TAG_ESCAPE_CHAR_LOOKUP_TABLE.update({
    ord(':'): ';',
    ord('s'): ' ',
    ord('r'): '\r',
    ord('n'): '\n',
})


def escape_tag_value(in_string: str) -> str:
    for key, val in TAG_VAL_TO_ESCAPE.items():
        in_string = in_string.replace(key, val)
    return in_string


def unescape_tag_value(in_string: str) -> str:
    if '\\' not in in_string:
        return in_string

    buf = []
    remainder = in_string
    while remainder:
        backslash_pos = remainder.find('\\')
        if backslash_pos == -1:
            buf.append(remainder)
            break
        elif backslash_pos == len(remainder) - 1:
            # Trailing backslash, which we strip
            buf.append(remainder[:-1])
            break

        buf.append(remainder[:backslash_pos])
        buf.append(TAG_ESCAPE_CHAR_LOOKUP_TABLE.get(ord(remainder[backslash_pos + 1]), remainder[backslash_pos + 1]))
        remainder = remainder[backslash_pos + 2:]

    return ''.join(buf)


def validate_tag_name(name: str) -> bool:
    if len(name) == 0:
        return False
    if name[0] == '+':
        name = name[1:]
    if len(name) == 0:
        return False
    # Let's err on the side of leniency here; allow -./ (45-47) in any position
    for c in name:  # noqa
        if not (('-' <= c <= '/') or ('0' <= c <= '9') or ('A' <= c <= 'Z') or ('a' <= c <= 'z')):
            return False
    return True


def validate_tag_value(value: str) -> bool:
    rt = value.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    return value == rt


def parse_tags(raw_tags: str) -> dict[str, str]:
    dct: dict[str, str] = {}

    while raw_tags:
        tag_end = raw_tags.find(';')
        if tag_end == -1:
            tag_pair = raw_tags
            raw_tags = ''
        else:
            tag_pair = raw_tags[:tag_end]
            raw_tags = raw_tags[tag_end + 1:]

        equals_index = tag_pair.find('=')
        if equals_index == -1:
            # Tag with no value
            tag_name, tag_value = tag_pair, ''
        else:
            tag_name, tag_value = tag_pair[:equals_index], tag_pair[equals_index + 1:]

        # "Implementations [...] MUST NOT perform any validation that would reject the message if an invalid tag key
        # name is used."
        if validate_tag_name(tag_name):
            if not validate_tag_value(tag_value):
                raise InvalidTagContentError
            dct[tag_name] = unescape_tag_value(tag_value)

    return dct
