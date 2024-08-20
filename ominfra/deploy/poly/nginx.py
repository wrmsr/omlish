import dataclasses as dc
import os.path
import textwrap
import typing as ta

from omlish.lite.cached import cached_nullary

from .base import DeployConcern
from .base import FsFile
from .base import FsItem
from .base import SiteConcern


class NginxSiteConcern(SiteConcern['NginxSiteConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(SiteConcern.Config):
        global_conf_file: str = '/etc/nginx/sites-enabled/omlish.conf'

    @cached_nullary
    def confs_dir(self) -> str:
        return os.path.join(self._site.config.root_dir, 'conf', 'nginx')

    def run(self) -> None:
        if self._site.runtime().stat(self._config.global_conf_file) is None:
            self._site.runtime().write_file(
                self._config.global_conf_file,
                f'include {self.confs_dir()}/*.conf;\n',
            )


class NginxDeployConcern(DeployConcern['NginxDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcern.Config):
        listen_port: int = 80
        proxy_port: int = 8000

    @cached_nullary
    def conf_file(self) -> str:
        return os.path.join(self._deploy.site.concern(NginxSiteConcern).confs_dir(), self._deploy.config.name + '.conf')

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsFile(self.conf_file())]

    def run(self) -> None:
        self._deploy.runtime().make_dirs(os.path.dirname(self.conf_file()))

        conf = textwrap.dedent(f"""
            server {{
                listen {self._config.listen_port};
                location / {{
                    proxy_pass http://127.0.0.1:{self._config.proxy_port}/;
                }}
            }}
        """)

        self._deploy.runtime().write_file(self.conf_file(), conf)
