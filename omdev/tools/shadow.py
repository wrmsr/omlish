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
from omlish.subprocesses.editor import get_user_text_editor

from ..cli.types import CliModule
from ..home.shadow import get_file_shadow_configs
from ..home.shadow import get_shadow_paths


##


class ShadowCli(ap.Cli):
    @ap.cmd(
        ap.arg('-p', '--path'),
    )
    def pwd(self) -> None:
        print(get_shadow_paths().get_shadow_path(self._args.path or os.getcwd()))

    #

    def _get_shadow_file(
            self,
            name: str,
            *,
            path: str | None = None,
            preferred_ext: str | None = None,
    ) -> str | None:
        return get_file_shadow_configs().get_shadow_config_file_path(
            path if path is not None else os.getcwd(),
            name,
            preferred_ext=preferred_ext,
        )

    @ap.cmd(
        ap.arg('name'),
        ap.arg('-p', '--path'),
        ap.arg('-x', '--preferred-ext', default='yml'),
    )
    def edit(self) -> None:
        shd_file = check.not_none(self._get_shadow_file(
            self._args.name,
            path=self._args.path,
            preferred_ext=self._args.preferred_ext,
        ))
        os.makedirs(os.path.dirname(shd_file), exist_ok=True)

        ed = get_user_text_editor()
        ed_exe = check.not_none(shutil.which(ed))

        os.execl(ed_exe, ed_exe, shd_file)

    @ap.cmd(
        ap.arg('name'),
        ap.arg('-p', '--path'),
    )
    def show(self) -> None:
        shd_file = self._get_shadow_file(
            self._args.name,
            path=self._args.path,
        )
        if not shd_file:
            return
        try:
            with open(shd_file) as f:
                buf = f.read()
        except FileNotFoundError:
            return
        print(buf)

    @ap.cmd(
        ap.arg('name'),
        ap.arg('-p', '--path'),
        ap.arg('-x', '--preferred-ext'),
    )
    def which(self) -> None:
        shd_file = self._get_shadow_file(
            self._args.name,
            path=self._args.path,
            preferred_ext=self._args.preferred_ext,
        )
        if shd_file is not None:
            print(shd_file)


##


# @omlish-manifest
_CLI_MODULE = CliModule('shadow', __name__)


def _main() -> None:
    ShadowCli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
