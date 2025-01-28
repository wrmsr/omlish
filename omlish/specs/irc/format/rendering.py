import typing as ta

from .consts import MAX_LEN_CLIENT_TAG_DATA
from .consts import MAX_LEN_SERVER_TAG_DATA
from .consts import MAX_LEN_TAGS_FROM_CLIENT
from .errors import BadCharactersError
from .errors import BadParamError
from .errors import CommandMissingError
from .errors import InvalidTagContentError
from .errors import TagsTooLongError
from .message import Message
from .tags import escape_tag_value
from .tags import validate_tag_name
from .tags import validate_tag_value
from .utils import find_utf8_truncation_point


def param_requires_trailing(param: str) -> bool:
    return len(param) == 0 or ' ' in param or param[0] == ':'


class RenderedLine(ta.NamedTuple):
    raw: bytes

    truncated: bool = False


def render_line_(
        msg: Message,
        *,
        tag_limit: int | None = None,
        client_only_tag_data_limit: int | None = None,
        server_added_tag_data_limit: int | None = None,
        truncate_len: int | None = None,
) -> RenderedLine:
    if not msg.command:
        raise CommandMissingError

    buf = bytearray()
    len_regular_tags = len_client_only_tags = 0

    # Write the tags, computing the budgets for client-only tags and regular tags
    if msg.tags or msg.client_only_tags:
        buf.append(ord('@'))
        first_tag = True
        tag_error = None

        def write_tags(tags: ta.Mapping[str, str]) -> None:
            nonlocal first_tag, tag_error
            for tag, val in tags.items():
                if not (validate_tag_name(tag) and validate_tag_value(val)):
                    tag_error = InvalidTagContentError
                if not first_tag:
                    buf.append(ord(';'))
                buf.extend(tag.encode('utf-8'))
                if val:
                    buf.append(ord('='))
                    buf.extend(escape_tag_value(val).encode('utf-8'))
                first_tag = False

        write_tags(msg.tags or {})
        len_regular_tags = len(buf) - 1
        write_tags(msg.client_only_tags or {})
        len_client_only_tags = (len(buf) - 1) - len_regular_tags
        if len_regular_tags:
            # Semicolon between regular and client-only tags is not counted
            len_client_only_tags -= 1
        buf.append(ord(' '))
        if tag_error:
            raise tag_error

    len_tags = len(buf)
    if tag_limit is not None and len(buf) > tag_limit:
        raise TagsTooLongError
    if (
            (client_only_tag_data_limit is not None and len_client_only_tags > client_only_tag_data_limit) or
            (server_added_tag_data_limit is not None and len_regular_tags > server_added_tag_data_limit)
    ):
        raise TagsTooLongError

    if msg.source:
        buf.append(ord(':'))
        buf.extend(msg.source.encode('utf-8'))
        buf.append(ord(' '))

    buf.extend(msg.command.encode('utf-8'))

    for i, param in enumerate(msg.params):
        buf.append(ord(' '))
        requires_trailing = param_requires_trailing(param)
        last_param = i == len(msg.params) - 1

        if (requires_trailing or msg.force_trailing) and last_param:
            buf.append(ord(':'))
        elif requires_trailing and not last_param:
            raise BadParamError

        buf.extend(param.encode('utf-8'))

    # Truncate if desired; leave 2 bytes over for \r\n:
    truncated = False
    if truncate_len is not None and (truncate_len - 2) < (len(buf) - len_tags):
        truncated = True
        new_buf_len = len_tags + (truncate_len - 2)
        buf = buf[:find_utf8_truncation_point(buf, new_buf_len)]

    buf.extend(b'\r\n')

    to_validate = buf[:-2]
    if any(c in to_validate for c in (b'\x00', b'\r', b'\n')):
        raise BadCharactersError

    raw = bytes(buf)

    return RenderedLine(
        raw=raw,
        truncated=truncated,
    )


def render_line(msg: Message) -> bytes:
    return render_line_(msg).raw


def render_line_strict(
        msg: Message,
        from_client: bool,
        truncate_len: int | None,
) -> RenderedLine:
    tag_limit: int | None = None
    client_only_tag_data_limit: int | None = None
    server_added_tag_data_limit: int | None = None
    if from_client:
        # enforce client max tags:
        # <client_max>   (4096)  :: '@' <tag_data 4094> ' '
        tag_limit = MAX_LEN_TAGS_FROM_CLIENT
    else:
        # on the server side, enforce separate client-only and server-added tag budgets:
        # "Servers MUST NOT add tag data exceeding 4094 bytes to messages."
        # <combined_max> (8191)  :: '@' <tag_data 4094> ';' <tag_data 4094> ' '
        client_only_tag_data_limit = MAX_LEN_CLIENT_TAG_DATA
        server_added_tag_data_limit = MAX_LEN_SERVER_TAG_DATA

    return render_line_(
        msg,
        tag_limit=tag_limit,
        client_only_tag_data_limit=client_only_tag_data_limit,
        server_added_tag_data_limit=server_added_tag_data_limit,
        truncate_len=truncate_len,
    )
