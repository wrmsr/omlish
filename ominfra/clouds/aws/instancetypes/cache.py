import bz2
import typing as ta

from omcore import lang
from omcore.formats.json import all as json


##


@lang.cached_function()
def load_instance_types() -> ta.Mapping[str, ta.Mapping[str, ta.Any]]:
    raw = lang.get_relative_resources(globals=globals())['cache.json.bz2'].read_bytes()
    data = bz2.decompress(raw)
    return json.loads(data)
