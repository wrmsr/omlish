"""
TODO:
 - default run bash
 - all of the below stuff

====

if [ -t 1 ] ; then
   TTY_ENV_ARGS="-e LINES=$(tput lines) -e COLUMNS=$(tput cols)"
else
   TTY_ENV_ARGS=""
fi

SERVICE_NAME="$(basename "$SCRIPT_DIR")-dev"
if ! [ $# -eq 0 ] ; then
    if [ "$1" = "--amd64" ] ; then
        SERVICE_NAME="$SERVICE_NAME-amd64"
        shift
    fi
fi

CONTAINER_ID=$(docker-compose -f 'docker/compose.yml' ps -q "$SERVICE_NAME")
if [ -z "$CONTAINER_ID" ] ; then
    echo "$SERVICE_NAME not running" 1>&2
    exit 1
fi

if [ -z "$DOCKER_HOST_PLATFORM" ] ; then
    if [ $(uname) = "Linux" ] ; then
        DOCKER_HOST_PLATFORM=linux
    elif [ $(uname) = "Darwin" ] ; then
        DOCKER_HOST_PLATFORM=darwin
    fi
fi

exec docker exec \
    $TTY_ENV_ARGS \
    -e DOCKER_HOST_PLATFORM="$DOCKER_HOST_PLATFORM" \
    --privileged \
    --detach-keys 'ctrl-o,ctrl-d' \
    -it "$CONTAINER_ID" \
    "$@"
"""
import os.path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap

from .gen import Config
from .gen import gen_src


##


SHA_PAT = re.compile(r'sha256:[0-9a-f]{64}')


def run_and_tee(cmd: ta.Sequence[str]) -> tuple[subprocess.Popen, str]:
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # merge stderr into stdout
        bufsize=1,
        text=True,  # decode to str
    )

    captured = []

    for line in check.not_none(proc.stdout):
        sys.stdout.write(line)
        sys.stdout.flush()
        captured.append(line)

    proc.wait()

    return proc, ''.join(captured)


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

    def _build(
            self,
            cfg: Config | None = None,
            *,
            verbose: bool = False,
    ) -> str:
        if cfg is None:
            cfg = self._load_config()

        src = gen_src(cfg)

        tmp_dir = tempfile.mkdtemp()
        df = os.path.join(tmp_dir, 'Dockerfile')
        with open(df, 'w') as f:
            f.write(src)

        build_args = ['-f', df, '.']

        if not verbose:
            out = subprocess.check_output(['docker', 'build', '-q', *build_args]).decode()
            if (m := SHA_PAT.search(out)) is not None:
                return m.group(0)
            raise RuntimeError('Can\'t find sha256 in output')

        else:
            proc, out = run_and_tee(['docker', 'build', *build_args])
            check.state(proc.returncode == 0)
            for line in reversed(out.splitlines()):
                if (m := SHA_PAT.search(line)) is not None:
                    return m.group(0)
            raise RuntimeError('Can\'t find sha256 in output')

    @ap.cmd(
        ap.arg('-v', '--verbose', action='store_true'),
        ap.arg('args', nargs=ap.REMAINDER),
    )
    def build(self) -> None:
        sha = self._build(
            verbose=self.args.verbose,
        )

        print(sha)

    @ap.cmd(
        ap.arg('-v', '--verbose', action='store_true'),
        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
    )
    def run(self) -> None:
        check.not_empty(self.args.args)

        sha = self._build(
            verbose=self.args.verbose,
        )

        os.execl(
            docker := check.not_none(shutil.which('docker')),
            docker,
            'run',
            *(
                self.unknown_args or
                [
                    '--rm',
                    '-it',
                ]
            ),
            sha,
            *self.args.args,
        )


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
