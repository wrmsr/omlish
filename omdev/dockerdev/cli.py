"""
TODO:
 - (run) profiles
   - auto mount r/o git share
 - autoexec - multiple options
   - can run 'bash -c 'barf barf barf && <user stuff>'
     - or mount temp dir and exec a file in there
   - can fast-build new (temp) image w preamble (probably slow and garbagey)
 - all of the below stuff
 - launch / manage compose services
 - more cache dirs
 - --mount=type=bind,src="$(pwd)",dst=/omlish/pwd
   - --mount=type=bind,src=/host/dir,dst=/container/dir,readonly (git)
 - build --no-cache / cache bust
   - build args
 - auto go/zig vers
 - `run --pull=never`, `build --pull=false`

====

if [ -t 1 ] ; then TTY_ENV_ARGS="-e LINES=$(tput lines) -e COLUMNS=$(tput cols)" ; fi
--detach-keys 'ctrl-o,ctrl-d' \
"""
import json
import os.path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.os.paths import is_path_in_dir

from ..home.paths import get_cache_dir
from .config import Config
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
            offline: bool = False,
            verbose: bool = False,
    ) -> str:
        if cfg is None:
            cfg = self._load_config()

        #

        bim = cfg.base_image
        for sep in ':@':
            bim = bim.split(sep, maxsplit=1)[0]

        def run_insp() -> str:
            return subprocess.check_output([  # type: ignore
                'docker', 'image', 'inspect', cfg.base_image],  # type: ignore[union-attr]
                **(dict(stderr=subprocess.DEVNULL) if not verbose else {}),
            ).decode()

        try:
            insp_out = run_insp()
        except subprocess.CalledProcessError:
            if offline:
                raise
            subprocess.check_output(['docker', 'pull', '-q', cfg.base_image])
            insp_out = run_insp()

        insp_out_obj = json.loads(insp_out)
        insp_out_dct = check.not_empty(insp_out_obj)[0]

        obi = check.non_empty_str(insp_out_dct['RepoDigests'][0])
        cfg = dc.replace(cfg, base_image=obi)

        #

        src = gen_src(cfg)

        tmp_dir = tempfile.mkdtemp()
        df = os.path.join(tmp_dir, 'Dockerfile')
        with open(df, 'w') as f:
            f.write(src)

        build_args = [
            '-f',
            df,
        ]

        if offline:
            build_args.append('--pull=false')

        build_args.append('.')

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

        ap.arg('--mount', action='append'),
        ap.arg('-C', '--mount-caches', action='store_true'),
        ap.arg('-D', '--mount-docker-sock', action='store_true'),

        ap.arg('-P', '--privileged', action='store_true'),

        ap.arg('-O', '--offline', action='store_true'),

        ap.arg('--no-host-platform', action='store_true'),

        ap.arg('-x', '--autoexec', action='append'),

        ap.arg('-X', '--x11', action='store_true'),

        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
    )
    def run(self) -> None:
        cfg = self._load_config()

        #

        sha = self._build(
            cfg,
            offline=self.args.offline,
            verbose=self.args.verbose,
        )

        #

        run_args: list[str] = ['run']

        if self.unknown_args:
            run_args.extend(self.unknown_args)
        else:
            run_args.extend([
                '--rm',
                '-it',
            ])

        if self.args.privileged:
            run_args.append('--privileged')

        if self.args.offline:
            run_args.append('--pull=never')

        if self.args.mount:
            run_args.extend([f'--mount={m}' for m in self.args.mount])

        if self.args.mount_docker_sock:
            run_args.append('--mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock')

        if self.args.mount_caches:
            cache_dir = os.path.join(get_cache_dir(), 'dockerdev')
            for cl, cr in (cfg.cache_mounts or {}).items():
                cld = os.path.join(cache_dir, cl)
                check.state(is_path_in_dir(cache_dir, cld))
                os.makedirs(cld, exist_ok=True)
                run_args.append(f'--mount=type=bind,src={cld},dst={cr}')

        if not self.args.no_host_platform:
            run_args.extend([f'--env=DOCKER_HOST_PLATFORM={platform.system().lower()}'])

        if self.args.autoexec:
            tmp_dir = tempfile.mkdtemp()
            tmp_ep = os.path.join(tmp_dir, 'entrypoint.sh')
            with open(tmp_ep, 'w') as f:
                f.write('\n'.join([
                    '#!/bin/sh',
                    'set -e',
                    *self.args.autoexec,
                    'exec "$@"',
                ]))
            os.chmod(tmp_ep, 0o755)  # noqa
            run_args.extend([
                f'--mount=type=bind,src={tmp_dir},dst=/dockerdev,readonly',
                f'--entrypoint=/dockerdev/entrypoint.sh',
            ])

        if self.args.x11:
            sys_platform = getattr(sys, 'platform')  # shuts up mypy
            if sys_platform.startswith('linux'):
                run_args.extend([
                    f'--env=DISPLAY',
                    '--volume=/tmp/.X11-unix:/tmp/.X11-unix:rw',
                    f'--volume={os.environ["HOME"]}/.Xauthority:/tmp/.Xauthority:ro',
                    '--env=XAUTHORITY=/tmp/.Xauthority',
                ])
            elif sys_platform == 'darwin':
                run_args.extend([
                    '--env=DISPLAY=host.docker.internal:0',
                ])
            else:
                raise OSError(sys_platform)

        run_args.append(sha)

        if self.args.args:
            run_args.extend(check.not_empty(self.args.args))
        else:
            run_args.append('bash')

        #

        os.execl(
            docker := check.not_none(shutil.which('docker')),
            docker,
            *run_args,
        )


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
