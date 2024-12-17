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

from .paths import DEPLOY_PATH_PLACEHOLDER_SEPARATOR
from .paths import SingleDirDeployPathOwner
from .specs import AppDeployConfLink
from .specs import DeployConfFile
from .specs import DeployConfLink
from .specs import DeployConfSpec
from .specs import TagDeployConfLink
from .types import DeployAppTag
from .types import DeployHome


class DeployConfManager(SingleDirDeployPathOwner):
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome] = None,
    ) -> None:
        super().__init__(
            owned_dir='conf',
            deploy_home=deploy_home,
        )

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

    async def _make_conf_link(
            self,
            link: DeployConfLink,
            conf_dir: str,
            app_tag: DeployAppTag,
            link_dir: str,
    ) -> None:
        link_src = os.path.join(conf_dir, link.src)
        check.arg(is_path_in_dir(conf_dir, link_src))

        is_link_dir = link.src.endswith('/')
        if is_link_dir:
            check.arg(link.src.count('/') == 1)
            check.arg(os.path.isdir(link_src))
            link_dst_pfx = link.src
            link_dst_sfx = ''

        elif '/' in link.src:
            check.arg(os.path.isfile(link_src))
            d, f = os.path.split(link.src)
            # TODO: check filename :|
            link_dst_pfx = d + '/'
            link_dst_sfx = '-' + f

        else:
            check.arg(os.path.isfile(link_src))
            if '.' in link.src:
                l, _, r = link.src.partition('.')
                link_dst_pfx = l + '/'
                link_dst_sfx = '.' + r
            else:
                link_dst_pfx = link.src + '/'
                link_dst_sfx = ''

        if isinstance(link, AppDeployConfLink):
            link_dst_mid = str(app_tag.app)
            sym_root = link_dir
        elif isinstance(link, TagDeployConfLink):
            link_dst_mid = DEPLOY_PATH_PLACEHOLDER_SEPARATOR.join([app_tag.app, app_tag.tag])
            sym_root = conf_dir
        else:
            raise TypeError(link)

        link_dst = ''.join([
            link_dst_pfx,
            link_dst_mid,
            link_dst_sfx,
        ])

        root_conf_dir = self._make_dir()
        sym_src = os.path.join(sym_root, link.src)
        sym_dst = os.path.join(root_conf_dir, link_dst)
        check.arg(is_path_in_dir(root_conf_dir, sym_dst))

        os.makedirs(os.path.dirname(sym_dst), exist_ok=True)
        relative_symlink(sym_src, sym_dst, target_is_directory=is_link_dir)

    async def write_conf(
            self,
            spec: DeployConfSpec,
            conf_dir: str,
            app_tag: DeployAppTag,
            link_dir: str,
    ) -> None:
        conf_dir = os.path.abspath(conf_dir)
        os.makedirs(conf_dir)

        #

        for cf in spec.files or []:
            await self._write_conf_file(
                cf,
                conf_dir,
            )

        #

        for link in spec.links or []:
            await self._make_conf_link(
                link,
                conf_dir,
                app_tag,
                link_dir,
            )
