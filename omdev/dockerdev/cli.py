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
import tomllib

from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap

from .build import build_image
from .config import Config
from .gen import gen_src
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
        ap.arg('-G', '--mount-git', action='store_true'),

        ap.arg('-P', '--privileged', action='store_true'),

        ap.arg('-O', '--offline', action='store_true'),

        ap.arg('--no-host-platform', action='store_true'),

        ap.arg('-x', '--autoexec', action='append'),

        ap.arg('-X', '--x11', action='store_true'),

        ap.arg('--shift-uid'),

        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
    )
    def run(self) -> None:
        run_image(
            self._load_config(),

            RunArgs(
                verbose=bool(self.args.verbose),

                mounts=self.args.mount,
                mount_caches=bool(self.args.mount_caches),
                mount_docker_sock=bool(self.args.mount_docker_sock),
                mount_git=bool(self.args.mount_git),

                privileged=bool(self.args.privileged),

                offline=bool(self.args.offline),

                no_host_platform=bool(self.args.no_host_platform),

                autoexecs=self.args.autoexec,

                x11=bool(self.args.x11),

                shift_uid=tuple(map(int, su.split(':'))) if (su := self.args.shift_uid) is not None else None,  # type: ignore[arg-type]  # noqa

                unknown_args=self.unknown_args,
                extra_args=self.args.args,
            ),
        )


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
