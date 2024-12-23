# ruff: noqa: UP006 UP007
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

    async def prepare_app(
            self,
            spec: DeployAppSpec,
            home: DeployHome,
            tags: DeployTagMap,
    ) -> str:
        spec_json = json_dumps_pretty(self._msh.marshal_obj(spec))

        #

        check.non_empty_str(home)

        app_dir = os.path.join(home, self.APP_DIR.render(tags))

        os.makedirs(app_dir, exist_ok=True)

        #

        spec_file = os.path.join(app_dir, 'spec.json')
        with open(spec_file, 'w') as f:
            f.write(spec_json)

        #

        app_git_dir = os.path.join(app_dir, 'git')
        await self._git.checkout(
            spec.git,
            home,
            app_git_dir,
        )

        #

        if spec.venv is not None:
            app_venv_dir = os.path.join(app_dir, 'venv')
            await self._venvs.setup_venv(
                spec.venv,
                home,
                app_git_dir,
                app_venv_dir,
            )

        #

        if spec.conf is not None:
            app_conf_dir = os.path.join(app_dir, 'conf')
            await self._conf.write_app_conf(
                spec.conf,
                app_conf_dir,
            )

        #

        return app_dir
