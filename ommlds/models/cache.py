import bz2
import typing as ta

from omlish import lang
from omlish.formats.json import all as json


##


@lang.cached_function()
def load_models() -> ta.Mapping[str, ta.Mapping[str, ta.Any]]:
    raw = lang.get_relative_resources(globals=globals())['cache.json.bz2'].read_bytes()
    data = bz2.decompress(raw)
    return json.loads(data)
