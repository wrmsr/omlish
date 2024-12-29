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
import collections.abc
import functools
import os.path
import typing as ta

from omlish.configs.nginx import NginxConfigItems
from omlish.configs.nginx import render_nginx_config_str
from omlish.formats.ini.sections import render_ini_sections
from omlish.lite.check import check
from omlish.lite.json import json_dumps_pretty
from omlish.lite.strings import strip_with_newline
from omlish.os.paths import is_path_in_dir
from omlish.os.paths import relative_symlink

from ..paths.paths import DeployPath
from ..tags import DEPLOY_TAG_SEPARATOR
from ..tags import DeployApp
from ..tags import DeployConf
from ..tags import DeployTagMap
from .specs import DeployAppConfContent
from .specs import DeployAppConfFile
from .specs import DeployAppConfLink
from .specs import DeployAppConfSpec
from .specs import IniDeployAppConfContent
from .specs import JsonDeployAppConfContent
from .specs import NginxDeployAppConfContent
from .specs import RawDeployAppConfContent


T = ta.TypeVar('T')


##


class DeployConfManager:
    def _process_conf_content(
            self,
            content: T,
            *,
            str_processor: ta.Optional[ta.Callable[[str], str]] = None,
    ) -> T:
        def rec(o):
            if isinstance(o, str):
                if str_processor is not None:
                    return type(o)(str_processor(o))

            elif isinstance(o, collections.abc.Mapping):
                return type(o)([  # type: ignore
                    (rec(k), rec(v))
                    for k, v in o.items()
                ])

            elif isinstance(o, collections.abc.Iterable):
                return type(o)([  # type: ignore
                    rec(e) for e in o
                ])

            return o

        return rec(content)

    #

    def _render_app_conf_content(
            self,
            ac: DeployAppConfContent,
            *,
            str_processor: ta.Optional[ta.Callable[[str], str]] = None,
    ) -> str:
        pcc = functools.partial(
            self._process_conf_content,
            str_processor=str_processor,
        )

        if isinstance(ac, RawDeployAppConfContent):
            return pcc(ac.body)

        elif isinstance(ac, JsonDeployAppConfContent):
            json_obj = pcc(ac.obj)
            return strip_with_newline(json_dumps_pretty(json_obj))

        elif isinstance(ac, IniDeployAppConfContent):
            ini_sections = pcc(ac.sections)
            return strip_with_newline(render_ini_sections(ini_sections))

        elif isinstance(ac, NginxDeployAppConfContent):
            nginx_items = NginxConfigItems.of(pcc(ac.items))
            return strip_with_newline(render_nginx_config_str(nginx_items))

        else:
            raise TypeError(ac)

    async def _write_app_conf_file(
            self,
            acf: DeployAppConfFile,
            app_conf_dir: str,
            *,
            str_processor: ta.Optional[ta.Callable[[str], str]] = None,
    ) -> None:
        conf_file = os.path.join(app_conf_dir, acf.path)
        check.arg(is_path_in_dir(app_conf_dir, conf_file))

        body = self._render_app_conf_content(
            acf.content,
            str_processor=str_processor,
        )

        os.makedirs(os.path.dirname(conf_file), exist_ok=True)

        with open(conf_file, 'w') as f:  # noqa
            f.write(body)

    async def write_app_conf(
            self,
            spec: DeployAppConfSpec,
            app_conf_dir: str,
            *,
            string_ns: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> None:
        process_str: ta.Any
        if string_ns is not None:
            def process_str(s: str) -> str:
                return s.format(**string_ns)
        else:
            process_str = None

        for acf in spec.files or []:
            await self._write_app_conf_file(
                acf,
                app_conf_dir,
                str_processor=process_str,
            )

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

    async def link_app_conf(
            self,
            spec: DeployAppConfSpec,
            tags: DeployTagMap,
            app_conf_dir: str,
            conf_link_dir: str,
    ):
        for link in spec.links or []:
            await self._make_app_conf_link(
                link,
                tags,
                app_conf_dir,
                conf_link_dir,
            )
