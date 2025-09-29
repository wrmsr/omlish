import typing as ta

from ... import check
from ... import lang
from ... import marshal as msh
from .keywords.base import Keywords
from .keywords.parse import KeywordParser
from .keywords.render import render_keywords


##


class _KeywordsMarshaler(msh.Marshaler):
    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        return render_keywords(check.isinstance(o, Keywords))


class _KeywordsUnmarshaler(msh.Unmarshaler):
    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        return KeywordParser(allow_unknown=True).parse_keywords(check.isinstance(v, ta.Mapping))


@lang.static_init
def _install_standard_marshaling() -> None:
    msh.install_standard_factories(
        msh.TypeMapMarshalerFactory({Keywords: _KeywordsMarshaler()}),
        msh.TypeMapUnmarshalerFactory({Keywords: _KeywordsUnmarshaler()}),
    )
