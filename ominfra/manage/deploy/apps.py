# ruff: noqa: UP006 UP007
import datetime
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.os.paths import relative_symlink

from .conf import DeployConfManager
from .git import DeployGitManager
from .paths.owners import DeployPathOwner
from .paths.paths import DeployPath
from .specs import DeploySpec
from .types import DeployAppTag
from .types import DeployHome
from .types import DeployKey
from .types import DeployRev
from .types import DeployTag
from .venvs import DeployVenvManager


def make_deploy_tag(
        rev: DeployRev,
        key: DeployKey,
        *,
        utcnow: ta.Optional[datetime.datetime] = None,
) -> DeployTag:
    if utcnow is None:
        utcnow = datetime.datetime.now(tz=datetime.timezone.utc)  # noqa
    now_fmt = '%Y%m%dT%H%M%SZ'
    now_str = utcnow.strftime(now_fmt)
    return DeployTag('-'.join([now_str, rev, key]))


class DeployAppManager(DeployPathOwner):
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome] = None,

            conf: DeployConfManager,
            git: DeployGitManager,
            venvs: DeployVenvManager,
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home

        self._conf = conf
        self._git = git
        self._venvs = venvs

    #

    _APP_TAG_DIR_STR = 'tags/apps/@app/@tag/'
    _APP_TAG_DIR = DeployPath.parse(_APP_TAG_DIR_STR)

    _CONF_TAG_DIR_STR = 'tags/conf/@tag--@app/'
    _CONF_TAG_DIR = DeployPath.parse(_CONF_TAG_DIR_STR)

    _DEPLOY_DIR_STR = 'deploys/@tag--@app/'
    _DEPLOY_DIR = DeployPath.parse(_DEPLOY_DIR_STR)

    _APP_DEPLOY_LINK = DeployPath.parse(f'{_DEPLOY_DIR_STR}apps/@app')
    _CONF_DEPLOY_LINK = DeployPath.parse(f'{_DEPLOY_DIR_STR}conf')

    @cached_nullary
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            self._APP_TAG_DIR,

            self._CONF_TAG_DIR,

            self._DEPLOY_DIR,

            self._APP_DEPLOY_LINK,
            self._CONF_DEPLOY_LINK,

            *[
                DeployPath.parse(f'{self._APP_TAG_DIR_STR}{sfx}/')
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
            spec: DeploySpec,
    ) -> None:
        app_tag = DeployAppTag(spec.app, make_deploy_tag(spec.git.rev, spec.key()))

        #

        deploy_home = check.non_empty_str(self._deploy_home)

        def build_path(pth: DeployPath) -> str:
            return os.path.join(deploy_home, pth.render(app_tag.placeholders()))

        app_tag_dir = build_path(self._APP_TAG_DIR)
        conf_tag_dir = build_path(self._CONF_TAG_DIR)
        deploy_dir = build_path(self._DEPLOY_DIR)
        app_deploy_link = build_path(self._APP_DEPLOY_LINK)
        conf_deploy_link_file = build_path(self._CONF_DEPLOY_LINK)

        #

        os.makedirs(deploy_dir)

        deploying_link = os.path.join(deploy_home, 'deploys/deploying')
        relative_symlink(
            deploy_dir,
            deploying_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        os.makedirs(app_tag_dir)
        relative_symlink(
            app_tag_dir,
            app_deploy_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        os.makedirs(conf_tag_dir)
        relative_symlink(
            conf_tag_dir,
            conf_deploy_link_file,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        git_dir = os.path.join(app_tag_dir, 'git')
        await self._git.checkout(
            spec.git,
            git_dir,
        )

        #

        if spec.venv is not None:
            venv_dir = os.path.join(app_tag_dir, 'venv')
            await self._venvs.setup_venv(
                spec.venv,
                git_dir,
                venv_dir,
            )

        #

        if spec.conf is not None:
            conf_dir = os.path.join(app_tag_dir, 'conf')
            await self._conf.write_conf(
                spec.conf,
                app_tag,
                conf_dir,
                conf_tag_dir,
            )

        #

        current_link = os.path.join(deploy_home, 'deploys/current')
        os.replace(deploying_link, current_link)
