# ruff: noqa: UP006 UP007
"""
TODO:
 - @conf DeployPathPlaceholder? :|
 - post-deploy: remove any dir_links not present in new spec
  - * only if succeeded * - otherwise, remove any dir_links present in new spec but not previously present?
   - no such thing as 'previously present'.. build a 'deploy state' and pass it back?
 - ** whole thing can be atomic **
  - 1) new atomic temp dir
  - 2) for each subdir not needing modification, hardlink into temp dir
  - 3) for each subdir needing modification, new subdir, hardlink all files not needing modification
  - 4) write (or if deleting, omit) new files
  - 5) swap top level
 - ** whole deploy can be atomic(-ish) - do this for everything **
  - just a '/deploy/current' dir
  - some things (venvs) cannot be moved, thus the /deploy/venvs dir
  - ** ensure (enforce) equivalent relpath nesting
"""
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.os.paths import is_path_in_dir
from omlish.os.paths import relative_symlink

from .paths.paths import DEPLOY_PATH_PLACEHOLDER_SEPARATOR
from .specs import AppDeployConfLink
from .specs import DeployConfFile
from .specs import DeployConfLink
from .specs import DeployConfSpec
from .specs import TagDeployConfLink
from .types import DeployAppTag
from .types import DeployHome


class DeployConfManager:
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome] = None,
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home

    #

    async def _write_conf_file(
            self,
            cf: DeployConfFile,
            conf_dir: str,
    ) -> None:
        conf_file = os.path.join(conf_dir, cf.path)
        check.arg(is_path_in_dir(conf_dir, conf_file))

        os.makedirs(os.path.dirname(conf_file), exist_ok=True)

        with open(conf_file, 'w') as f:  # noqa
            f.write(cf.body)

    #

    class _ComputedConfLink(ta.NamedTuple):
        is_dir: bool
        link_src: str
        link_dst: str
        sym_root: str

    def _compute_conf_link_dst(
            self,
            link: DeployConfLink,
            app_tag: DeployAppTag,
            conf_dir: str,
            link_dir: str,
    ) -> _ComputedConfLink:
        link_src = os.path.join(conf_dir, link.src)
        check.arg(is_path_in_dir(conf_dir, link_src))

        #

        if (is_dir := link.src.endswith('/')):
            # @conf/ - links a directory in root of app conf dir to conf/@conf/@dst/
            check.arg(link.src.count('/') == 1)
            link_dst_pfx = link.src
            link_dst_sfx = ''

        elif '/' in link.src:
            # @conf/file - links a single file in a single subdir to conf/@conf/@dst-file
            d, f = os.path.split(link.src)
            # TODO: check filename :|
            link_dst_pfx = d + '/'
            link_dst_sfx = '-' + f

        else:  # noqa
            # @conf(.ext)* - links a single file in root of app conf dir to conf/@conf/@dst(.ext)*
            if '.' in link.src:
                l, _, r = link.src.partition('.')
                link_dst_pfx = l + '/'
                link_dst_sfx = '.' + r
            else:
                link_dst_pfx = link.src + '/'
                link_dst_sfx = ''

        #

        if isinstance(link, AppDeployConfLink):
            link_dst_mid = str(app_tag.app)
            sym_root = link_dir
        elif isinstance(link, TagDeployConfLink):
            link_dst_mid = DEPLOY_PATH_PLACEHOLDER_SEPARATOR.join([app_tag.app, app_tag.tag])
            sym_root = conf_dir
        else:
            raise TypeError(link)

        #

        link_dst = ''.join([
            link_dst_pfx,
            link_dst_mid,
            link_dst_sfx,
        ])

        return DeployConfManager._ComputedConfLink(
            is_dir=is_dir,
            link_src=link_src,
            link_dst=link_dst,
            sym_root=sym_root,
        )

    async def _make_conf_link(
            self,
            link: DeployConfLink,
            app_tag: DeployAppTag,
            conf_dir: str,
            link_dir: str,
    ) -> None:
        comp = self._compute_conf_link_dst(
            link,
            app_tag,
            conf_dir,
            link_dir,
        )

        #

        if comp.is_dir:
            check.arg(os.path.isdir(comp.link_src))
        else:
            check.arg(os.path.isfile(comp.link_src))

        #

        sym_src = os.path.join(comp.sym_root, link.src)
        sym_dst = os.path.join(conf_dir, comp.link_dst)
        check.arg(is_path_in_dir(conf_dir, sym_dst))

        raise NotImplementedError

        relative_symlink(  # noqa
            sym_src,
            sym_dst,
            target_is_directory=comp.is_dir,
            make_dirs=True,
        )

    #

    async def write_conf(
            self,
            spec: DeployConfSpec,
            app_tag: DeployAppTag,
            conf_dir: str,
            link_dir: str,
    ) -> None:
        for cf in spec.files or []:
            await self._write_conf_file(
                cf,
                conf_dir,
            )

        #

        for link in spec.links or []:
            await self._make_conf_link(
                link,
                app_tag,
                conf_dir,
                link_dir,
            )
