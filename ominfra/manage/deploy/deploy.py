# ruff: noqa: UP006 UP007
import datetime
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check
from omlish.lite.json import json_dumps_pretty
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.typing import Func0
from omlish.lite.typing import Func1
from omlish.os.paths import relative_symlink

from .apps import DeployAppManager
from .paths.manager import DeployPathsManager
from .paths.owners import DeployPathOwner
from .paths.paths import DeployPath
from .specs import DeployAppSpec
from .specs import DeploySpec
from .tags import DeployAppRev
from .tags import DeployTagMap
from .tags import DeployTime
from .types import DeployHome


##


DEPLOY_TAG_DATETIME_FMT = '%Y%m%dT%H%M%SZ'


DeployManagerUtcClock = ta.NewType('DeployManagerUtcClock', Func0[datetime.datetime])


class DeployManager(DeployPathOwner):
    def __init__(
            self,
            *,
            utc_clock: ta.Optional[DeployManagerUtcClock] = None,
    ):
        super().__init__()

        self._utc_clock = utc_clock

    #

    DEPLOYS_DIR = DeployPath.parse('deploys/')

    CURRENT_DEPLOY_LINK = DeployPath.parse(f'{DEPLOYS_DIR}current')
    DEPLOYING_DEPLOY_LINK = DeployPath.parse(f'{DEPLOYS_DIR}deploying')

    DEPLOY_DIR = DeployPath.parse(f'{DEPLOYS_DIR}@time--@deploy-key/')
    DEPLOY_SPEC_FILE = DeployPath.parse(f'{DEPLOY_DIR}spec.json')

    APPS_DEPLOY_DIR = DeployPath.parse(f'{DEPLOY_DIR}apps/')
    APP_DEPLOY_LINK = DeployPath.parse(f'{APPS_DEPLOY_DIR}@app')

    CONF_DEPLOY_DIR = DeployPath.parse(f'{DEPLOY_DIR}conf/@conf/')

    @cached_nullary
    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            self.DEPLOYS_DIR,

            self.CURRENT_DEPLOY_LINK,
            self.DEPLOYING_DEPLOY_LINK,

            self.DEPLOY_DIR,
            self.DEPLOY_SPEC_FILE,

            self.APPS_DEPLOY_DIR,
            self.APP_DEPLOY_LINK,

            self.CONF_DEPLOY_DIR,
        }

    #

    def _utc_now(self) -> datetime.datetime:
        if self._utc_clock is not None:
            return self._utc_clock()  # noqa
        else:
            return datetime.datetime.now(tz=datetime.timezone.utc)  # noqa

    def make_deploy_time(self) -> DeployTime:
        return DeployTime(self._utc_now().strftime(DEPLOY_TAG_DATETIME_FMT))


##


class DeployDriverFactory(Func1[DeploySpec, ta.ContextManager['DeployDriver']]):
    pass


class DeployDriver:
    def __init__(
            self,
            *,
            spec: DeploySpec,
            home: DeployHome,
            time: DeployTime,

            deploys: DeployManager,
            paths: DeployPathsManager,
            apps: DeployAppManager,

            msh: ObjMarshalerManager,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._home = home
        self._time = time

        self._deploys = deploys
        self._paths = paths
        self._apps = apps

        self._msh = msh

    #

    @cached_nullary
    def deploy_tags(self) -> DeployTagMap:
        return DeployTagMap(
            self._time,
            self._spec.key(),
        )

    def render_deploy_path(self, pth: DeployPath) -> str:
        return os.path.join(self._home, pth.render(self.deploy_tags()))

    @property
    def deploy_dir(self) -> str:
        return self.render_deploy_path(self._deploys.DEPLOY_DIR)

    #

    async def drive_deploy(self) -> None:
        spec_json = json_dumps_pretty(self._msh.marshal_obj(self._spec))

        #

        self._paths.validate_deploy_paths()

        #

        os.makedirs(self.deploy_dir)

        #

        spec_file = self.render_deploy_path(self._deploys.DEPLOY_SPEC_FILE)
        with open(spec_file, 'w') as f:
            f.write(spec_json)

        #

        deploying_link = self.render_deploy_path(self._deploys.DEPLOYING_DEPLOY_LINK)
        if os.path.exists(deploying_link):
            os.unlink(deploying_link)
        relative_symlink(
            self.deploy_dir,
            deploying_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        deploy_conf_dir = os.path.join(deploy_dir, 'conf')
        os.makedirs(deploy_conf_dir, exist_ok=True)

        #

        spec_file = os.path.join(deploy_dir, 'spec.json')
        with open(spec_file, 'w') as f:
            f.write(spec_json)

        #

        for app in self._spec.apps:
            await self.drive_app_deploy(app)

    #

    async def drive_app_deploy(self, app: DeployAppSpec) -> None:
        app_tags = self.deploy_tags.add(
            app.app,
            app.key(),
            DeployAppRev(app.git.rev),
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

        await self._apps.prepare_app(
            app,
            self._home,
            app_tags,
        )
