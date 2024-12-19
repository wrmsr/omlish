# ruff: noqa: UP006 UP007
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.os.paths import relative_symlink

from .conf import DeployConfManager
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
            conf: DeployConfManager,
            git: DeployGitManager,
            venvs: DeployVenvManager,
    ) -> None:
        super().__init__()

        self._conf = conf
        self._git = git
        self._venvs = venvs

    #

    _APP_DIR_STR = 'apps/@app/@time--@app-rev--@app-key/'
    _APP_DIR = DeployPath.parse(_APP_DIR_STR)

    _DEPLOY_DIR_STR = 'deploys/@time--@deploy-key/'
    _DEPLOY_DIR = DeployPath.parse(_DEPLOY_DIR_STR)

    _APP_DEPLOY_LINK = DeployPath.parse(f'{_DEPLOY_DIR_STR}apps/@app')
    _CONF_DEPLOY_DIR = DeployPath.parse(f'{_DEPLOY_DIR_STR}conf/@conf/')

    @cached_nullary
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            self._APP_DIR,

            self._DEPLOY_DIR,

            self._APP_DEPLOY_LINK,
            self._CONF_DEPLOY_DIR,

            *[
                DeployPath.parse(f'{self._APP_DIR_STR}{sfx}/')
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
    ) -> None:
        check.non_empty_str(home)

        def build_path(pth: DeployPath) -> str:
            return os.path.join(home, pth.render(tags))

        app_dir = build_path(self._APP_DIR)
        deploy_dir = build_path(self._DEPLOY_DIR)
        app_deploy_link = build_path(self._APP_DEPLOY_LINK)

        #

        os.makedirs(deploy_dir, exist_ok=True)

        deploying_link = os.path.join(home, 'deploys/deploying')
        if os.path.exists(deploying_link):
            os.unlink(deploying_link)
        relative_symlink(
            deploy_dir,
            deploying_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        os.makedirs(app_dir)
        relative_symlink(
            app_dir,
            app_deploy_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        deploy_conf_dir = os.path.join(deploy_dir, 'conf')
        os.makedirs(deploy_conf_dir, exist_ok=True)

        #

        # def mirror_symlinks(src: str, dst: str) -> None:
        #     def mirror_link(lp: str) -> None:
        #         check.state(os.path.islink(lp))
        #         shutil.copy2(
        #             lp,
        #             os.path.join(dst, os.path.relpath(lp, src)),
        #             follow_symlinks=False,
        #         )
        #
        #     for dp, dns, fns in os.walk(src, followlinks=False):
        #         for fn in fns:
        #             mirror_link(os.path.join(dp, fn))
        #
        #         for dn in dns:
        #             dp2 = os.path.join(dp, dn)
        #             if os.path.islink(dp2):
        #                 mirror_link(dp2)
        #             else:
        #                 os.makedirs(os.path.join(dst, os.path.relpath(dp2, src)))

        current_link = os.path.join(home, 'deploys/current')

        # if os.path.exists(current_link):
        #     mirror_symlinks(
        #         os.path.join(current_link, 'conf'),
        #         conf_tag_dir,
        #     )
        #     mirror_symlinks(
        #         os.path.join(current_link, 'apps'),
        #         os.path.join(deploy_dir, 'apps'),
        #     )

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
                tags,
                app_conf_dir,
                deploy_conf_dir,
            )

        #

        os.replace(deploying_link, current_link)
