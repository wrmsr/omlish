"""
TODO:
 - (run) profiles
   - auto mount r/o git share
 - autoexec - multiple options
   - can run 'bash -c 'barf barf barf && <user stuff>'
     - or mount temp dir and exec a file in there
   - can fast-build new (temp) image w preamble (probably slow and garbagey)
 - launch / manage compose services
 - more cache dirs
 - --mount=type=bind,src="$(pwd)",dst=/omlish/pwd
 - build --no-cache / cache bust
   - build args
 - `run --pull=never`, `build --pull=false`
 - !! shadow config !!
   - default autoexec, default env vars

====

if [ -t 1 ] ; then TTY_ENV_ARGS="-e LINES=$(tput lines) -e COLUMNS=$(tput cols)" ; fi
--detach-keys 'ctrl-o,ctrl-d' \

====

tag = f'omlish-dockerdev--{time.time_ns()}--{os.getpid()}'
subprocess.check_call(['docker', 'tag', obi, tag])
try:
    cfg = dc.replace(cfg, base_image=tag)  # noqa
    ...
finally:
    subprocess.check_call(['docker', 'image', 'rm', tag], stdout=subprocess.DEVNULL)
"""
import os
import subprocess
import sys
import tomllib

from omcore import check
from omcore import lang
from omcore import marshal as msh
from omcore.argparse import all as ap

from .build import build_image
from .config import Config
from .gen import gen_src
from .run import LABEL_PREFIX
from .run import RunArgs
from .run import run_image


##


class Cli(ap.Cli):
    def _load_config(self) -> Config:
        cfg_src = lang.get_relative_resources(globals=globals())['config.toml'].read_text()
        cfg_dct = tomllib.loads(cfg_src)
        return msh.unmarshal(cfg_dct, Config)

    @ap.cmd()
    def gen(self) -> None:
        cfg = self._load_config()
        src = gen_src(cfg)
        print(src)

    #

    @ap.cmd(
        ap.arg('-v', '--verbose', action='store_true'),

        ap.arg('-O', '--offline', action='store_true'),
    )
    def build(self) -> None:
        sha = build_image(
            self._load_config(),

            offline=bool(self.args.offline),

            verbose=bool(self.args.verbose),
        )

        print(sha)

    @ap.cmd(
        ap.arg('-v', '--verbose', action='store_true'),

        ap.arg('--mount', action='append'),
        ap.arg('-C', '--mount-caches', action='store_true'),
        ap.arg('-D', '--mount-docker-sock', action='store_true'),
        ap.arg('--mount-git', action='store_true'),
        ap.arg('-G', '--clone-mount-git', action='store_true'),

        ap.arg('-P', '--privileged', action='store_true'),

        ap.arg('-O', '--offline', action='store_true'),

        ap.arg('--no-host-platform', action='store_true'),

        ap.arg('-x', '--autoexec', action='append'),

        ap.arg('-X', '--x11', action='store_true'),

        ap.arg('--inject-secrets', action='append'),

        ap.arg('--shift-uid'),
        ap.arg('-U', '--auto-shift-uid', action='store_true'),

        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
    )
    def run(self) -> None:
        shift_uid: tuple[int, int] | None = None
        if (su := self.args.shift_uid) is not None:
            check.arg(not self.args.auto_shift_uid)
            shift_uid = tuple(map(int, su.split(':')))  # type: ignore[assignment]
        elif self.args.auto_shift_uid:
            if getattr(sys, 'platform') == 'linux':
                shift_uid = (os.getuid(), os.getgid())

        run_image(
            self._load_config(),

            RunArgs(
                verbose=bool(self.args.verbose),

                mounts=self.args.mount,
                mount_caches=bool(self.args.mount_caches),
                mount_docker_sock=bool(self.args.mount_docker_sock),
                mount_git=bool(self.args.mount_git),
                clone_mount_git=bool(self.args.clone_mount_git),

                privileged=bool(self.args.privileged),

                offline=bool(self.args.offline),

                no_host_platform=bool(self.args.no_host_platform),

                autoexecs=self.args.autoexec,

                x11=bool(self.args.x11),

                inject_secrets_pats=self.args.inject_secrets,

                shift_uid=shift_uid,

                unknown_args=self.unknown_args,
                extra_args=self.args.args,
            ),
        )

    #

    @ap.cmd(
        ap.arg('-j', '--json', action='store_true'),

        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
    )
    def ps(self) -> None:
        out = subprocess.check_output([
            'docker',
            'ps',
            *(self.unknown_args or []),
            f'--filter=label={LABEL_PREFIX}',
            *(['--format=json'] if self.args.json else []),
            *(self.args.args or []),
        ])

        print(out.decode(), end='')


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
