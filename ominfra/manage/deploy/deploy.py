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
from .tags import DeployTagMap
from .tags import DeployTime
from .tmp import DeployHomeAtomics
from .types import DeployHome


##


DEPLOY_TAG_DATETIME_FMT = '%Y-%m-%d-T-%H-%M-%S-%f-Z'


DeployManagerUtcClock = ta.NewType('DeployManagerUtcClock', Func0[datetime.datetime])


class DeployManager(DeployPathOwner):
    def __init__(
            self,
            *,
            atomics: DeployHomeAtomics,

            utc_clock: ta.Optional[DeployManagerUtcClock] = None,
    ):
        super().__init__()

        self._atomics = atomics

        self._utc_clock = utc_clock

    #

    # Home current link just points to CURRENT_DEPLOY_LINK, and is intended for user convenience.
    HOME_CURRENT_LINK = DeployPath.parse('current')

    DEPLOYS_DIR = DeployPath.parse('deploys/')

    # Authoritative current symlink is not in deploy-home, just to prevent accidental corruption.
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

    def render_path(self, home: DeployHome, pth: DeployPath, tags: ta.Optional[DeployTagMap] = None) -> str:
        return os.path.join(check.non_empty_str(home), pth.render(tags))

    #

    def _utc_now(self) -> datetime.datetime:
        if self._utc_clock is not None:
            return self._utc_clock()  # noqa
        else:
            return datetime.datetime.now(tz=datetime.timezone.utc)  # noqa

    def make_deploy_time(self) -> DeployTime:
        return DeployTime(self._utc_now().strftime(DEPLOY_TAG_DATETIME_FMT))

    #

    def make_home_current_link(self, home: DeployHome) -> None:
        home_current_link = os.path.join(check.non_empty_str(home), self.HOME_CURRENT_LINK.render())
        current_deploy_link = os.path.join(check.non_empty_str(home), self.CURRENT_DEPLOY_LINK.render())
        with self._atomics(home).begin_atomic_path_swap(  # noqa
                'file',
                home_current_link,
                auto_commit=True,
        ) as dst_swap:
            os.unlink(dst_swap.tmp_path)
            os.symlink(
                os.path.relpath(current_deploy_link, os.path.dirname(dst_swap.dst_path)),
                dst_swap.tmp_path,
            )


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
    def tags(self) -> DeployTagMap:
        return DeployTagMap(
            self._time,
            self._spec.key(),
        )

    def render_path(self, pth: DeployPath, tags: ta.Optional[DeployTagMap] = None) -> str:
        return os.path.join(self._home, pth.render(tags if tags is not None else self.tags))

    @property
    def dir(self) -> str:
        return self.render_path(self._deploys.DEPLOY_DIR)

    #

    async def drive_deploy(self) -> None:
        spec_json = json_dumps_pretty(self._msh.marshal_obj(self._spec))

        #

        das: ta.Set[DeployApp] = {a.app for a in self._spec.apps}
        las: ta.Set[DeployApp] = set(self._spec.app_links.apps)
        ras: ta.Set[DeployApp] = set(self._spec.app_links.removed_apps)
        check.empty(das & (las | ras))
        check.empty(las & ras)

        #

        self._paths.validate_deploy_paths()

        #

        os.makedirs(self.dir)

        #

        spec_file = self.render_path(self._deploys.DEPLOY_SPEC_FILE)
        with open(spec_file, 'w') as f:  # noqa
            f.write(spec_json)

        #

        deploying_link = self.render_path(self._deploys.DEPLOYING_DEPLOY_LINK)
        current_link = self.render_path(self._deploys.CURRENT_DEPLOY_LINK)

        #

        if os.path.exists(deploying_link):
            os.unlink(deploying_link)
        relative_symlink(
            self.dir,
            deploying_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        for md in [
            self._deploys.APPS_DEPLOY_DIR,
            self._deploys.CONFS_DEPLOY_DIR,
        ]:
            os.makedirs(self.render_path(md))

        #

        if not self._spec.app_links.exclude_unspecified:
            cad = abs_real_path(os.path.join(current_link, 'apps'))
            if os.path.exists(cad):
                for d in os.listdir(cad):
                    if (da := DeployApp(d)) not in das and da not in ras:
                        las.add(da)

        for la in las:
            await self._drive_app_link(
                la,
                current_link,
            )

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
            os.path.join(self.dir, 'conf', 'systemd'),  # FIXME
        )

        #

        self._deploys.make_home_current_link(self._home)

    #

    async def _drive_app_deploy(self, app: DeployAppSpec) -> None:
        current_deploy_link = os.path.join(self._home, self._deploys.CURRENT_DEPLOY_LINK.render())

        pa = await self._apps.prepare_app(
            app,
            self._home,
            self.tags,
            conf_string_ns=dict(
                deploy_home=self._home,
                current_deploy_link=current_deploy_link,
            ),
        )

        #

        app_link = self.render_path(self._deploys.APP_DEPLOY_LINK, pa.tags)
        relative_symlink(
            pa.dir,
            app_link,
            target_is_directory=True,
            make_dirs=True,
        )

        #

        await self._drive_app_configure(pa)

    async def _drive_app_link(
            self,
            app: DeployApp,
            current_link: str,
    ) -> None:
        app_link = os.path.join(abs_real_path(current_link), 'apps', app.s)
        check.state(os.path.islink(app_link))

        app_dir = abs_real_path(app_link)
        check.state(os.path.isdir(app_dir))

        #

        pa = await self._apps.prepare_app_link(
            self.tags,
            app_dir,
        )

        #

        relative_symlink(
            app_dir,
            os.path.join(self.dir, 'apps', app.s),
            target_is_directory=True,
        )

        #

        await self._drive_app_configure(pa)

    async def _drive_app_configure(
            self,
            pa: DeployAppManager.PreparedApp,
    ) -> None:
        deploy_conf_dir = self.render_path(self._deploys.CONFS_DEPLOY_DIR)
        if pa.spec.conf is not None:
            await self._conf.link_app_conf(
                pa.spec.conf,
                pa.tags,
                check.non_empty_str(pa.conf_dir),
                deploy_conf_dir,
            )
