# Copyright (c) 2016-2021 Daniel Oaks
# Copyright (c) 2018-2021 Shivaram Lingamneni
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby
# granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
# AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
# https://github.com/ergochat/irc-go/blob/9beac2d29dc5f998c5a53e5db7a6426d7d083a79/ircmsg/
from .consts import (  # noqa
    MAX_LEN_CLIENT_TAG_DATA,
    MAX_LEN_SERVER_TAG_DATA,
    MAX_LEN_TAGS,
    MAX_LEN_TAGS_FROM_CLIENT,
    MAX_LEN_TAG_DATA,
)

from .errors import (  # noqa
    BadCharactersError,
    BadParamError,
    CommandMissingError,
    Error,
    InvalidTagContentError,
    LineEmptyError,
    MalformedNuhError,
    TagsTooLongError,
)

from .message import (  # noqa
    Message,
)

from .nuh import (  # noqa
    Nuh,
)

from .parsing import (  # noqa
    ParsedLine,
    parse_line,
    parse_line_,
    parse_line_strict,
)

from .rendering import (  # noqa
    RenderedLine,
    render_line,
    render_line_,
    render_line_strict,
)

from .tags import (  # noqa
    escape_tag_value,
    parse_tags,
    unescape_tag_value,
    validate_tag_name,
    validate_tag_value,
)
