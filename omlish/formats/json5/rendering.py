import typing as ta

from ..json import Scalar
from ..json.literals import ESCAPE_MAP
from ..json.literals import encode_string
from ..json.literals import encode_string_ascii
from ..json.rendering import JsonRenderer
from ..json.rendering import JsonRendererOut


##


MULTILINE_STRINGS_ESCAPE_MAP = {
    **ESCAPE_MAP,
    '\n': '\\n\\\n',
}


class Json5Renderer(JsonRenderer):
    def __init__(
            self,
            out: JsonRendererOut,
            *,
            multiline_strings: bool = False,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(out, **kwargs)

        self._multiline_strings = multiline_strings

    def _format_scalar(self, o: Scalar) -> str:
        if (
                self._multiline_strings and
                isinstance(o, str) and
                '\n' in o
        ):
            if self._ensure_ascii:
                return encode_string_ascii(o, escape_map=MULTILINE_STRINGS_ESCAPE_MAP)
            else:
                return encode_string(o, escape_map=MULTILINE_STRINGS_ESCAPE_MAP)

        else:
            return super()._format_scalar(o)
