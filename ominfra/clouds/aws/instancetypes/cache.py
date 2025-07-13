import gzip
import typing as ta

from omlish import lang
from omlish.formats import json


##


@lang.cached_function()
def load_instance_types() -> ta.Mapping[str, ta.Mapping[str, ta.Any]]:
    raw = lang.get_relative_resources(globals=globals())['cache.json.gz'].read_bytes()
    data = gzip.decompress(raw)
    return json.loads(data)
