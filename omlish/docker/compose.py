"""
TODO:
 - merged compose configs: https://github.com/wrmsr/bane/blob/27647abdcfb323b73e6982a5c318c7029496b203/core/dev/docker/compose.go#L38
"""  # noqa
import typing as ta

from .. import check
from .. import lang


if ta.TYPE_CHECKING:
    import yaml
else:
    yaml = lang.proxy_import('yaml')


class ComposeConfig:
    def __init__(
            self,
            prefix: str,
            *,
            file_path: str | None = None,
    ) -> None:
        super().__init__()

        self._prefix = prefix
        self._file_path = file_path

    @lang.cached_function
    def get_config(self) -> ta.Mapping[str, ta.Any]:
        with open(check.not_none(self._file_path)) as f:
            buf = f.read()
        return yaml.safe_load(buf)

    @lang.cached_function
    def get_services(self) -> ta.Mapping[str, ta.Any]:
        ret = {}
        for n, c in self.get_config()['services'].items():
            check.state(n.startswith(self._prefix))
            ret[n[len(self._prefix):]] = c

        return ret


def get_compose_port(cfg: ta.Mapping[str, ta.Any], default: int) -> int:
    return check.single(
        int(l)
        for p in cfg['ports']
        for l, r in [p.split(':')]
        if int(r) == default
    )
