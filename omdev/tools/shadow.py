"""
TODO:
 - 'edit', default cwd - use git's
 - delete?
 - 'purge'?
 - 'validate' - at least formats
"""
import os.path
import shutil

from omlish import check
from omlish.argparse import all as ap
from omlish.configs.shadow import FileShadowConfigs
from omlish.subprocesses.editor import get_user_text_editor

from ..cli.types import CliModule
from ..home.shadow import get_shadow_configs


##


class ShadowCli(ap.Cli):
    def _get_shadow_file(self, path: str | None = None) -> str:
        if (path := self._args.path) is None:
            path = os.getcwd()
        file_scs = check.isinstance(get_shadow_configs(), FileShadowConfigs)
        shd_file = file_scs.get_shadow_config_file_path(path)
        return shd_file

    #

    @ap.cmd(
        ap.arg('path', nargs='?'),
    )
    def edit(self) -> None:
        shd_file = self._get_shadow_file(self._args.path)
        os.makedirs(os.path.dirname(shd_file), exist_ok=True)

        ed = get_user_text_editor()
        ed_exe = check.not_none(shutil.which(ed))

        os.execl(ed_exe, ed_exe, shd_file)

    @ap.cmd(
        ap.arg('path', nargs='?'),
    )
    def show(self) -> None:
        shd_file = self._get_shadow_file(self._args.path)
        try:
            with open(shd_file) as f:
                buf = f.read()
        except FileNotFoundError:
            return
        print(buf)

    @ap.cmd(
        ap.arg('path', nargs='?'),
    )
    def which(self) -> None:
        shd_file = self._get_shadow_file(self._args.path)
        print(shd_file)


##


# @omlish-manifest
_CLI_MODULE = CliModule('shadow', __name__)


def _main() -> None:
    ShadowCli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
