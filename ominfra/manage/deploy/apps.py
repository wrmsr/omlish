# ruff: noqa: UP006 UP007
import datetime
import itertools
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.os.paths import relative_symlink

from .conf import DeployConfManager
from .git import DeployGitManager
from .paths import DeployPath
from .paths import DeployPathOwner
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

    _APP_TAG_PATH_STR = 'tags/apps/@app--@tag/'
    _APP_TAG_PATH = DeployPath.parse(_APP_TAG_PATH_STR)

    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            *itertools.chain.from_iterable([
                DeployPath.parse(f'{pfx}/apps/@app'),
                DeployPath.parse(f'{pfx}/conf/@conf'),
            ] for pfx in [
                'current',
                'deploying',
            ]),

            self._APP_TAG_PATH,

            *[
                DeployPath.parse(f'{self._APP_TAG_PATH_STR}/{sfx}/')
                for sfx in [
                    'conf',
                    'git',
                    'venv',
                ]
            ],

            DeployPath.parse('tags/conf/@conf--@app--@tag'),
        }

    async def prepare_app(
            self,
            spec: DeploySpec,
    ) -> None:
        app_tag = DeployAppTag(spec.app, make_deploy_tag(spec.git.rev, spec.key()))

        #

        self._APP_TAG_PATH.render(app_tag.placeholders())

        app_dir = os.path.join(check.non_empty_str(self._deploy_home), 'tags', 'apps', spec.app)
        os.makedirs(app_dir, exist_ok=True)

        #

        tag_dir = os.path.join(app_dir, 'tags', app_tag.tag)
        os.makedirs(tag_dir)

        #

        deploying_file = os.path.join(app_dir, 'deploying')
        current_file = os.path.join(app_dir, 'current')

        if os.path.exists(deploying_file):
            os.unlink(deploying_file)
        relative_symlink(tag_dir, deploying_file, target_is_directory=True)

        #

        git_dir = os.path.join(tag_dir, 'git')
        await self._git.checkout(
            spec.git,
            git_dir,
        )

        #

        if spec.venv is not None:
            venv_dir = os.path.join(tag_dir, 'venv')
            await self._venvs.setup_venv(
                spec.venv,
                git_dir,
                venv_dir,
            )

        #

        if spec.conf is not None:
            conf_dir = os.path.join(tag_dir, 'conf')
            conf_link_dir = os.path.join(current_file, 'conf')
            await self._conf.write_conf(
                spec.conf,
                conf_dir,
                app_tag,
                conf_link_dir,
            )

        #

        os.replace(deploying_file, current_file)
