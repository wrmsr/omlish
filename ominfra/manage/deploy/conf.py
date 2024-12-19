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

from .paths.paths import DeployPath
from .specs import DeployAppConfFile
from .specs import DeployAppConfLink
from .specs import DeployAppConfSpec
from .tags import DEPLOY_TAG_SEPARATOR
from .tags import DeployApp
from .tags import DeployConf
from .tags import DeployTagMap


class DeployConfManager:
    async def _write_app_conf_file(
            self,
            acf: DeployAppConfFile,
            app_conf_dir: str,
    ) -> None:
        conf_file = os.path.join(app_conf_dir, acf.path)
        check.arg(is_path_in_dir(app_conf_dir, conf_file))

        os.makedirs(os.path.dirname(conf_file), exist_ok=True)

        with open(conf_file, 'w') as f:  # noqa
            f.write(acf.body)

    #

    class _ComputedConfLink(ta.NamedTuple):
        conf: DeployConf
        is_dir: bool
        link_src: str
        link_dst: str

    _UNIQUE_LINK_NAME_STR = '@app--@time--@app-key'
    _UNIQUE_LINK_NAME = DeployPath.parse(_UNIQUE_LINK_NAME_STR)

    @classmethod
    def _compute_app_conf_link_dst(
            cls,
            link: DeployAppConfLink,
            tags: DeployTagMap,
            app_conf_dir: str,
            conf_link_dir: str,
    ) -> _ComputedConfLink:
        link_src = os.path.join(app_conf_dir, link.src)
        check.arg(is_path_in_dir(app_conf_dir, link_src))

        #

        if (is_dir := link.src.endswith('/')):
            # @conf/ - links a directory in root of app conf dir to conf/@conf/@dst/
            check.arg(link.src.count('/') == 1)
            conf = DeployConf(link.src.split('/')[0])
            link_dst_pfx = link.src
            link_dst_sfx = ''

        elif '/' in link.src:
            # @conf/file - links a single file in a single subdir to conf/@conf/@dst--file
            d, f = os.path.split(link.src)
            # TODO: check filename :|
            conf = DeployConf(d)
            link_dst_pfx = d + '/'
            link_dst_sfx = DEPLOY_TAG_SEPARATOR + f

        else:  # noqa
            # @conf(.ext)* - links a single file in root of app conf dir to conf/@conf/@dst(.ext)*
            if '.' in link.src:
                l, _, r = link.src.partition('.')
                conf = DeployConf(l)
                link_dst_pfx = l + '/'
                link_dst_sfx = '.' + r
            else:
                conf = DeployConf(link.src)
                link_dst_pfx = link.src + '/'
                link_dst_sfx = ''

        #

        if link.kind == 'current_only':
            link_dst_mid = str(tags[DeployApp].s)
        elif link.kind == 'all_active':
            link_dst_mid = cls._UNIQUE_LINK_NAME.render(tags)
        else:
            raise TypeError(link)

        #

        link_dst_name = ''.join([
            link_dst_pfx,
            link_dst_mid,
            link_dst_sfx,
        ])
        link_dst = os.path.join(conf_link_dir, link_dst_name)

        return DeployConfManager._ComputedConfLink(
            conf=conf,
            is_dir=is_dir,
            link_src=link_src,
            link_dst=link_dst,
        )

    async def _make_app_conf_link(
            self,
            link: DeployAppConfLink,
            tags: DeployTagMap,
            app_conf_dir: str,
            conf_link_dir: str,
    ) -> None:
        comp = self._compute_app_conf_link_dst(
            link,
            tags,
            app_conf_dir,
            conf_link_dir,
        )

        #

        check.arg(is_path_in_dir(app_conf_dir, comp.link_src))
        check.arg(is_path_in_dir(conf_link_dir, comp.link_dst))

        if comp.is_dir:
            check.arg(os.path.isdir(comp.link_src))
        else:
            check.arg(os.path.isfile(comp.link_src))

        #

        relative_symlink(  # noqa
            comp.link_src,
            comp.link_dst,
            target_is_directory=comp.is_dir,
            make_dirs=True,
        )

    #

    async def write_app_conf(
            self,
            spec: DeployAppConfSpec,
            tags: DeployTagMap,
            app_conf_dir: str,
            conf_link_dir: str,
    ) -> None:
        for acf in spec.files or []:
            await self._write_app_conf_file(
                acf,
                app_conf_dir,
            )

        #

        for link in spec.links or []:
            await self._make_app_conf_link(
                link,
                tags,
                app_conf_dir,
                conf_link_dir,
            )
