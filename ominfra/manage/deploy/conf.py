# ruff: noqa: UP006 UP007
"""
TODO:
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

from .paths import SingleDirDeployPathOwner
from .specs import DeployConfSpec
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

    async def write_conf(
            self,
            spec: DeployConfSpec,
            conf_dir: str,
            app_tag: DeployAppTag,
            link_dir: str,
    ) -> None:
        conf_dir = os.path.abspath(conf_dir)
        os.makedirs(conf_dir)

        for cf in spec.files or []:
            conf_file = os.path.join(conf_dir, cf.path)
            check.arg(is_path_in_dir(conf_dir, conf_file))

            os.makedirs(os.path.dirname(conf_file), exist_ok=True)

            with open(conf_file, 'w') as f:  # noqa
                f.write(cf.body)

        for dl in spec.dir_links:
            cdd = os.path.join(self._make_dir(), dl)
            check.arg(is_path_in_dir(self._make_dir(), cdd))
            os.makedirs(cdd, exist_ok=True)

            link_src = os.path.join(link_dir, dl)
            link_dst = os.path.join(cdd, app_tag.app)
            relative_symlink(link_src, link_dst)
