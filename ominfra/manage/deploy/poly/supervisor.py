import dataclasses as dc
import os.path
import textwrap
import typing as ta

from omlish.lite.cached import cached_nullary

from .base import DeployConcern
from .base import FsFile
from .base import FsItem
from .base import Runtime
from .configs import DeployConcernConfig
from .repo import RepoDeployConcern
from .venv import VenvDeployConcern


# class SupervisorSiteConcern(SiteConcern['SupervisorSiteConcern.Config']):
#     @dc.dataclass(frozen=True)
#     class Config(DeployConcern.Config):
#         global_conf_file: str = '/etc/supervisor/conf.d/supervisord.conf'
#
#     def run(self) -> None:
#         sup_conf_dir = os.path.join(self._d.home_dir(), 'conf/supervisor')
#         with open(self._d.host_cfg.global_supervisor_conf_file_path) as f:
#             glo_sup_conf = f.read()
#         if sup_conf_dir not in glo_sup_conf:
#             log.info('Updating global supervisor conf at %s', self._d.host_cfg.global_supervisor_conf_file_path)  # noqa
#             glo_sup_conf += textwrap.dedent(f"""
#                 [include]
#                 files = {self._d.home_dir()}/conf/supervisor/*.conf
#             """)
#             with open(self._d.host_cfg.global_supervisor_conf_file_path, 'w') as f:
#                 f.write(glo_sup_conf)


class SupervisorDeployConcern(DeployConcern['SupervisorDeployConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(DeployConcernConfig):
        entrypoint: str

    @cached_nullary
    def conf_file(self) -> str:
        return os.path.join(self._deploy.site.config.root_dir, 'conf', 'supervisor', self._deploy.config.name + '.conf')

    @cached_nullary
    def fs_items(self) -> ta.Sequence[FsItem]:
        return [FsFile(self.conf_file())]

    def run(self, runtime: Runtime) -> None:
        runtime.make_dirs(os.path.dirname(self.conf_file()))

        rd = self._deploy.concern(RepoDeployConcern).repo_dir()
        vx = self._deploy.concern(VenvDeployConcern).exe()

        conf = textwrap.dedent(f"""
            [program:{self._deploy.config.name}]
            command={vx} -m {self._config.entrypoint}
            directory={rd}
            user={self._deploy.site.config.user}
            autostart=true
            autorestart=true
        """)

        runtime.write_file(self.conf_file(), conf)
