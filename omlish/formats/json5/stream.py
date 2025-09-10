"""
Objects:
 + Object keys may be an ECMAScript 5.1 IdentifierName.
 + Objects may have a single trailing comma.
Arrays:
 + Arrays may have a single trailing comma.
Strings:
 + Strings may be single quoted.
 + Strings may span multiple lines by escaping new line characters.
 + Strings may include character escapes.
Numbers:
 + Numbers may be hexadecimal.
 + Numbers may have a leading or trailing decimal point.
 + Numbers may be IEEE 754 positive infinity, negative infinity, and NaN.
 + Numbers may begin with an explicit plus sign.
Comments:
 + Single and multi-line comments are allowed.
White Space:
 + Additional white space characters are allowed.
"""
from ..json.stream.building import JsonValueBuilder
from ..json.stream.lexing import JsonStreamLexer
from ..json.stream.parsing import JsonStreamParser
from ..json.stream.utils import JsonStreamValueParser
from .literals import parse_number_literal
from .literals import parse_string_literal


##


class Json5StreamValueParser(JsonStreamValueParser):
    def _make(self) -> tuple[
        JsonStreamLexer,
        JsonStreamParser,
        JsonValueBuilder,
    ]:
        return (
            JsonStreamLexer(
                include_raw=self._include_raw,

                allow_extended_space=True,

                allow_comments=True,

                allow_single_quotes=True,
                string_literal_parser=parse_string_literal,

                allow_extended_number_literals=True,
                number_literal_parser=parse_number_literal,

                allow_extended_idents=True,
            ),

            JsonStreamParser(
                allow_trailing_commas=True,

                allow_extended_idents=True,
            ),

            JsonValueBuilder(
                yield_object_lists=self._yield_object_lists,
            ),
        )


stream_parse_values = Json5StreamValueParser.parse_values
stream_parse_one_value = Json5StreamValueParser.parse_one_value
stream_parse_exactly_one_value = Json5StreamValueParser.parse_exactly_one_value
