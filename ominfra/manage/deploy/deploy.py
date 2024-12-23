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
from omlish.os.paths import abs_real_path
from omlish.os.paths import relative_symlink

from .apps import DeployAppManager
from .conf.manager import DeployConfManager
from .paths.manager import DeployPathsManager
from .paths.owners import DeployPathOwner
from .paths.paths import DeployPath
from .specs import DeployAppSpec
from .specs import DeploySpec
from .systemd import DeploySystemdManager
from .tags import DeployApp
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

    CONFS_DEPLOY_DIR = DeployPath.parse(f'{DEPLOY_DIR}conf/')
    CONF_DEPLOY_DIR = DeployPath.parse(f'{CONFS_DEPLOY_DIR}@conf/')

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

            self.CONFS_DEPLOY_DIR,
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
            conf: DeployConfManager,
            systemd: DeploySystemdManager,

            msh: ObjMarshalerManager,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._home = home
        self._time = time

        self._deploys = deploys
        self._paths = paths
        self._apps = apps
        self._conf = conf
        self._systemd = systemd

        self._msh = msh

    #

    @property
    def deploy_tags(self) -> DeployTagMap:
        return DeployTagMap(
            self._time,
            self._spec.key(),
        )

    def render_deploy_path(self, pth: DeployPath, tags: ta.Optional[DeployTagMap] = None) -> str:
        return os.path.join(self._home, pth.render(tags if tags is not None else self.deploy_tags))

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
        with open(spec_file, 'w') as f:  # noqa
            f.write(spec_json)

        #

        deploying_link = self.render_deploy_path(self._deploys.DEPLOYING_DEPLOY_LINK)
        current_link = self.render_deploy_path(self._deploys.CURRENT_DEPLOY_LINK)

        #

        if os.path.exists(deploying_link):
            os.unlink(deploying_link)
        relative_symlink(
            self.deploy_dir,
            deploying_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        for md in [
            self._deploys.APPS_DEPLOY_DIR,
            self._deploys.CONFS_DEPLOY_DIR,
        ]:
            os.makedirs(self.render_deploy_path(md))

        #

        for la in self._spec.app_links.apps:
            await self._drive_app_link(
                la,
                current_link,
            )

        #

        for app in self._spec.apps:
            await self._drive_app_deploy(
                app,
            )

        #

        os.replace(deploying_link, current_link)

        #

        await self._systemd.sync_systemd(
            self._spec.systemd,
            self._home,
            os.path.join(self.deploy_dir, 'conf', 'systemd'),  # FIXME
        )

    #

    async def _drive_app_deploy(self, app: DeployAppSpec) -> None:
        app_tags = self.deploy_tags.add(
            app.app,
            app.key(),
            DeployAppRev(app.git.rev),
        )

        #

        da = await self._apps.prepare_app(
            app,
            self._home,
            app_tags,
        )

        #

        app_link = self.render_deploy_path(self._deploys.APP_DEPLOY_LINK, app_tags)
        relative_symlink(
            da.app_dir,
            app_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        deploy_conf_dir = self.render_deploy_path(self._deploys.CONFS_DEPLOY_DIR)
        if app.conf is not None:
            await self._conf.link_app_conf(
                app.conf,
                app_tags,
                check.non_empty_str(da.conf_dir),
                deploy_conf_dir,
            )

    async def _drive_app_link(
            self,
            app: DeployApp,
            current_link: str,
    ) -> None:
        app_link = os.path.join(abs_real_path(current_link), 'apps', app.s)
        check.state(os.path.islink(app_link))

        app_dir = abs_real_path(app_link)
        check.state(os.path.isdir(app_dir))

        # relative_symlink(
        #     ad,
        #     os.path.join(self.deploy_dir, 'apps', la.s),  # FIXME: DeployPath
        #     target_is_directory=True,
        # )

        raise NotImplementedError
