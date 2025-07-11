import typing as ta

from ... import check
from ..json import Scalar
from ..json.literals import ESCAPE_MAP
from ..json.literals import encode_string
from ..json.rendering import JsonRenderer
from ..json.rendering import JsonRendererOut


##


MULTILINE_STRINGS_LQ = '"\\\n'
MULTILINE_STRINGS_RQ = '\\\n"'
MULTILINE_STRINGS_NL = '\\n\\\n'

MULTILINE_STRINGS_ESCAPE_MAP = {
    **ESCAPE_MAP,
    '\n': MULTILINE_STRINGS_NL,
}


class Json5Renderer(JsonRenderer):
    def __init__(
            self,
            out: JsonRendererOut,
            *,
            multiline_strings: bool = False,
            softwrap_length: int | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(out, **kwargs)

        self._multiline_strings = multiline_strings
        if softwrap_length is not None:
            check.arg(softwrap_length > 0)
        self._softwrap_length = softwrap_length

    def _format_scalar(self, o: Scalar, state: JsonRenderer.State | None = None) -> str:
        if isinstance(o, str):
            force_multiline = self._multiline_strings and '\n' in o

            if (sl := self._softwrap_length) is not None:
                def process_chunks(chunks: list[str]) -> list[str]:
                    if sum(map(len, chunks)) < sl:
                        if force_multiline:
                            return [
                                MULTILINE_STRINGS_LQ,
                                *[
                                    MULTILINE_STRINGS_NL if c == '\\n' else c
                                    for c in chunks
                                ],
                                MULTILINE_STRINGS_RQ,
                            ]

                        else:
                            return [
                                '"',
                                *chunks,
                                '"',
                            ]

                    raise NotImplementedError

                return encode_string(
                    o,
                    q='',
                    ensure_ascii=self._ensure_ascii,
                    process_chunks=process_chunks,
                )

            if force_multiline:
                return encode_string(
                    o,
                    lq=MULTILINE_STRINGS_LQ,
                    rq=MULTILINE_STRINGS_RQ,
                    escape_map=MULTILINE_STRINGS_ESCAPE_MAP,
                    ensure_ascii=self._ensure_ascii,
                )

        return super()._format_scalar(o)
