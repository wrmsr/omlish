import dataclasses as dc
import typing as ta


BaseServerUrl = ta.NewType('BaseServerUrl', str)


@dc.dataclass(frozen=True)
class UrlFor:
    base_server_url: BaseServerUrl

    def __call__(self, s: str) -> str:
        return self.base_server_url + s
