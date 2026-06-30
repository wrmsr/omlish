import bz2
import typing as ta

from omlish import lang
from omlish.formats.json import all as json


with lang.auto_proxy_import(globals()):
    from omlish import marshal as msh

    from . import types


##


@lang.cached_function()
def load_providers_raw() -> ta.Mapping[str, ta.Mapping[str, ta.Any]]:
    raw = lang.get_relative_resources(globals=globals())['cache.json.bz2'].read_bytes()
    data = bz2.decompress(raw)
    return json.loads(data)


@lang.cached_function()
def load_providers() -> ta.Mapping[str, types.Provider]:
    return msh.unmarshal(load_providers_raw(), ta.Mapping[str, types.Provider])  # type: ignore[call-overload]
