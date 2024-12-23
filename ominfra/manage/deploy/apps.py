# ruff: noqa: UP006 UP007
import dataclasses as dc
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.json import json_dumps_pretty
from omlish.lite.marshal import ObjMarshalerManager

from .conf.manager import DeployConfManager
from .git import DeployGitManager
from .paths.owners import DeployPathOwner
from .paths.paths import DeployPath
from .specs import DeployAppSpec
from .tags import DeployTagMap
from .types import DeployHome
from .venvs import DeployVenvManager


class DeployAppManager(DeployPathOwner):
    def __init__(
            self,
            *,
            git: DeployGitManager,
            venvs: DeployVenvManager,
            conf: DeployConfManager,

            msh: ObjMarshalerManager,
    ) -> None:
        super().__init__()

        self._git = git
        self._venvs = venvs
        self._conf = conf

        self._msh = msh

    #

    APP_DIR = DeployPath.parse('apps/@app/@time--@app-rev--@app-key/')

    @cached_nullary
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            self.APP_DIR,

            *[
                DeployPath.parse(f'{self.APP_DIR}{sfx}/')
                for sfx in [
                    'conf',
                    'git',
                    'venv',
                ]
            ],
        }

    #

    @dc.dataclass(frozen=True)
    class PreparedApp:
        app_dir: str

        git_dir: ta.Optional[str] = None
        venv_dir: ta.Optional[str] = None
        conf_dir: ta.Optional[str] = None

    async def prepare_app(
            self,
            spec: DeployAppSpec,
            home: DeployHome,
            tags: DeployTagMap,
    ) -> PreparedApp:
        spec_json = json_dumps_pretty(self._msh.marshal_obj(spec))

        #

        check.non_empty_str(home)

        app_dir = os.path.join(home, self.APP_DIR.render(tags))

        os.makedirs(app_dir, exist_ok=True)

        #

        rkw: ta.Dict[str, ta.Any] = dict(
            app_dir=app_dir,
        )

        #

        spec_file = os.path.join(app_dir, 'spec.json')
        with open(spec_file, 'w') as f:  # noqa
            f.write(spec_json)

        #

        git_dir = os.path.join(app_dir, 'git')
        rkw.update(git_dir=git_dir)
        await self._git.checkout(
            spec.git,
            home,
            git_dir,
        )

        #

        if spec.venv is not None:
            venv_dir = os.path.join(app_dir, 'venv')
            rkw.update(venv_dir=venv_dir)
            await self._venvs.setup_venv(
                spec.venv,
                git_dir,
                venv_dir,
            )

        #

        if spec.conf is not None:
            conf_dir = os.path.join(app_dir, 'conf')
            rkw.update(conf_dir=conf_dir)
            await self._conf.write_app_conf(
                spec.conf,
                conf_dir,
            )

        #

        return DeployAppManager.PreparedApp(**rkw)
