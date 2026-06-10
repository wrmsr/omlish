import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..params import ParamStyle
from ..syntax import QuoteStyle
from ..syntax import QuoteStyles


##


@dc.dataclass(frozen=True)
class Adapter(lang.Final):
    """
    Pure, io-less rendering configuration handed to a Renderer. Most dialect variation (quoting, param style) is
    expressed here as data - a Renderer subclass is only needed for genuine structural divergence.
    """

    param_style: ParamStyle | None = None
    quote_style: QuoteStyle = QuoteStyles.DOUBLE
    literal_style: ta.Literal['param_all', 'safe_only'] = 'safe_only'
