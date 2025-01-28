import typing as ta

from .consts import MAX_LEN_CLIENT_TAG_DATA
from .consts import MAX_LEN_TAG_DATA
from .errors import BadCharactersError
from .errors import LineEmptyError
from .errors import TagsTooLongError
from .message import Message
from .tags import parse_tags
from .utils import is_ascii
from .utils import trim_initial_spaces
from .utils import truncate_utf8_safe


class ParsedLine(ta.NamedTuple):
    message: Message

    truncated: bool = False


def parse_line_(
        line: str,
        *,
        max_tag_data_length: int | None = None,
        truncate_len: int | None = None,
) -> ParsedLine:
    # Remove either \n or \r\n from the end of the line:
    line = line.removesuffix('\n')
    line = line.removesuffix('\r')

    # Whether we removed them ourselves, or whether they were removed previously, they count against the line limit:
    if truncate_len is not None:
        if truncate_len <= 2:
            raise LineEmptyError
        truncate_len -= 2

    # Now validate for the 3 forbidden bytes:
    if any(c in line for c in '\x00\n\r'):
        raise BadCharactersError

    if not line:
        raise LineEmptyError

    #

    # Handle tags
    tags: ta.Mapping[str, str] | None = None
    if line.startswith('@'):
        tag_end = line.find(' ')
        if tag_end == -1:
            raise LineEmptyError
        raw_tags = line[1:tag_end]
        if max_tag_data_length is not None and len(raw_tags) > max_tag_data_length:
            raise TagsTooLongError
        tags = parse_tags(raw_tags)
        # Skip over the tags and the separating space
        line = line[tag_end + 1:]

    #

    # Truncate if desired
    truncated = False
    if truncate_len is not None and len(line) > truncate_len:
        line = truncate_utf8_safe(line, truncate_len)
        truncated = True

    line = trim_initial_spaces(line)

    # Handle source
    source: str | None = None

    if line.startswith(':'):
        source_end = line.find(' ')
        if source_end == -1:
            raise LineEmptyError
        source = line[1:source_end]
        line = line[source_end + 1:]

    # Modern: "These message parts, and parameters themselves, are separated by one or more ASCII SPACE characters"
    line = trim_initial_spaces(line)

    # Handle command
    command_end = line.find(' ')
    param_start = command_end + 1 if command_end != -1 else len(line)
    base_command = line[:command_end] if command_end != -1 else line

    if not base_command:
        raise LineEmptyError
    # Technically this must be either letters or a 3-digit numeric:
    if not is_ascii(base_command):
        raise BadCharactersError

    # Normalize command to uppercase:
    command = base_command.upper()
    line = line[param_start:]

    # Handle parameters
    params: list[str] = []
    while line:
        line = trim_initial_spaces(line)
        if not line:
            break
        # Handle trailing
        if line.startswith(':'):
            params.append(line[1:])
            break
        param_end = line.find(' ')
        if param_end == -1:
            params.append(line)
            break
        params.append(line[:param_end])
        line = line[param_end + 1:]

    #

    msg = Message(
        source=source,
        command=command,
        params=params,
        tags=tags,
    )

    return ParsedLine(
        msg,
        truncated=truncated,
    )


def parse_line(
        line: str,
        *,
        max_tag_data_length: int | None = None,
        truncate_len: int | None = None,
) -> Message:
    return parse_line_(
        line,
        max_tag_data_length=max_tag_data_length,
        truncate_len=truncate_len,
    ).message


def parse_line_strict(
        line: str,
        from_client: bool,
        truncate_len: int | None,
) -> ParsedLine:
    max_tag_data_length = MAX_LEN_TAG_DATA
    if from_client:
        max_tag_data_length = MAX_LEN_CLIENT_TAG_DATA

    return parse_line_(
        line,
        max_tag_data_length=max_tag_data_length,
        truncate_len=truncate_len,
    )
