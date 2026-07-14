from omlish import dataclasses as dc

from ..configs import ModuleConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class WebConfig(ModuleConfig):
    max_fetch_chars: int | None = None

    enable_search: bool = False
    max_search_results: int | None = None
