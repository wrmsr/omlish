"""
TODO:
 - https://github.com/zeromake/docker-debug
 - prune
  - docker container prune --force
  - docker system prune --all --force --filter "until=720h"
  - docker container prune --force --filter "until=720h"
  - docker image prune --all --force --filter "until=720h"
  - docker builder prune --all --force --filter "until=720h"
"""
import os
import re
import shutil
import subprocess
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.docker import all as dck
from omlish.formats import json
from omlish.formats import yaml
from omlish.logs import all as logs

from ..cli import CliModule


@lang.cached_function
def docker_exe() -> str:
    return check.not_none(shutil.which('docker'))


@lang.cached_function
def get_local_platform() -> str:
    return subprocess.check_output([
        docker_exe(),
        'system',
        'info',
        '--format',
        '{{.OSType}}/{{.Architecture}}',
    ]).decode().strip()


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('args', nargs='*'),
    )
    def ns1(self) -> None:
        """
        - https://gist.github.com/BretFisher/5e1a0c7bcca4c735e716abf62afad389
        - https://github.com/justincormack/nsenter1/blob/8d3ba504b2c14d73c70cf34f1ec6943c093f1b02/nsenter1.c

        alt:
         - nc -U ~/Library/Containers/com.docker.docker/Data/debug-shell.sock
        """

        os.execl(
            exe := docker_exe(),
            exe,
            'run',
            '--rm',
            '--platform', get_local_platform(),
            '--privileged',
            '--pid=host',
            '-it', 'debian',
            'nsenter',
            '-t', '1',
            '-m',  # mount
            '-u',  # uts
            '-i',  # ipc
            '-n',  # net
            '-p',  # pid
            '-C',  # cgroup
            # '-U',  # user
            '-T',  # time
            *self.args.args,
        )

    @ap.cmd(
        ap.arg('--amd64', action='store_true'),
    )
    def enable_ptrace(self) -> None:
        """
        - https://github.com/docker/for-mac/issues/5191
        - https://forums.docker.com/t/sys-ptrace-capability-for-linux-amd64/138482/4
        """

        os.execl(
            exe := docker_exe(),
            exe,
            'run',
            *(('--platform', 'linux/x86_64') if self.args.amd64 else ()),
            '--privileged',
            '-it', 'debian',
            'sh', '-c', 'echo 0 > /proc/sys/kernel/yama/ptrace_scope',
        )

    @ap.cmd(
        ap.arg('-f', '--file'),
        ap.arg('-w', '--write', action='store_true'),
        ap.arg('-q', '--quiet', action='store_true'),
        ap.arg('base', type=int),
    )
    def reset_compose_ports(self) -> None:
        base_port = int(self.args.base)
        if not base_port:
            raise Exception('Invalid base port')

        if self.args.file:
            yml_file = self.args.file
        else:
            yml_file = os.path.join('docker', 'compose.yml')

        with open(yml_file) as f:
            yml_src = f.read()

        #

        port_pat = re.compile(r'(?P<l>\d+):(?P<r>\d+)')
        port_line_pat = re.compile(r"(  )+- '(?P<l>\d+):(?P<r>\d+)'\s*")

        class PortEntry(ta.NamedTuple):
            l: int
            s: str

        dct: dict[str, list[PortEntry]] = {}

        with lang.disposing(yaml.WrappedLoaders.base(yml_src)) as loader:
            val = check.not_none(loader.get_single_data())  # type: ignore
            root = check.isinstance(val.value, ta.Mapping)

            services = check.isinstance(
                check.single(
                    v.value
                    for k, v in root.items()
                    if k.value == 'services'
                ),
                ta.Mapping,
            )
            for name_w, cfg_w in services.items():
                name = check.isinstance(name_w.value, str)
                cfg = check.isinstance(cfg_w.value, ta.Mapping)

                ports = check.opt_single(v.value for k, v in cfg.items() if k.value == 'ports')
                if not ports:
                    continue

                lst: list[PortEntry] = []
                for port_w in ports:
                    port = check.isinstance(port_w.value, str)
                    if not re.fullmatch(port_pat, port):
                        raise Exception(f'Bad port: {port}')

                    lst.append(PortEntry(
                        l=port_w.node.start_mark.line,
                        s=port,
                    ))

                dct[name] = lst

        #

        src_lines = yml_src.splitlines(keepends=True)
        cur_port = base_port

        for ps in dct.values():
            for p in ps:
                l = src_lines[p.l]
                if not (m := port_line_pat.fullmatch(l)):
                    raise Exception(f'Bad port line: {p} {l!r}')

                p_l, p_r = map(int, p.s.split(':'))
                l_l, l_r = map(int, [(gd := m.groupdict())['l'], gd['r']])
                if p_l != l_l or p_r != l_r:
                    raise Exception(f'Port mismatch: {p}')

                new_l = l.partition("'")[0] + f"'{cur_port}:{l_r}'\n"
                src_lines[p.l] = new_l

                cur_port += 1

        new_src = ''.join(src_lines)

        #

        if not self.args.quiet:
            print(new_src)

        if self.args.write:
            with open(yml_file, 'w') as f:
                f.write(new_src)

    @ap.cmd(
        ap.arg('repo'),
        ap.arg('tags', nargs='*'),
    )
    def repo_info(self) -> int:
        if (info := dck.get_hub_repo_info(self.args.repo, tags=self.args.tags or None)) is None:
            return 1
        print(json.dumps_pretty(msh.marshal(info)))
        return 0

    @ap.cmd(
        ap.arg('image'),
    )
    def repo_latest_image(self) -> int:
        if ':' in self.args.image:
            repo, _, base = self.args.image.partition(':')
        else:
            repo, base = self.args.image, None
        if (info := dck.get_hub_repo_info(repo)) is None:
            return 1
        print(dck.select_latest_tag(info.tags, base=base))
        return 0

    @ap.cmd(
        ap.arg('-f', '--file'),
    )
    def compose_image_updates(self) -> None:
        if self.args.file:
            yml_file = self.args.file
        else:
            yml_file = os.path.join('docker', 'compose.yml')

        with open(yml_file) as f:
            yml_src = f.read()

        cfg_dct = yaml.safe_load(yml_src)
        for svc_name, svc_dct in cfg_dct.get('services', {}).items():
            if not (img := svc_dct.get('image')):
                continue

            repo, _, base = img.partition(':')
            if (info := dck.get_hub_repo_info(repo)) is None:
                continue

            lt = dck.select_latest_tag(info.tags, base=base)
            if f'{repo}:{lt}' == img:
                continue

            print(f'{svc_name}: {lt}')

    #

    @ap.cmd()
    def dockly(self) -> None:
        os.execl(
            exe := docker_exe(),
            exe,
            'run', '-it', '--rm',
            '-v', '/var/run/docker.sock:/var/run/docker.sock',
            'lirantal/dockly',
        )

    @ap.cmd()
    def lazy(self) -> None:
        os.execl(
            exe := docker_exe(),
            exe,
            'run', '-it', '--rm',
            '-v', '/var/run/docker.sock:/var/run/docker.sock',
            'lazyteam/lazydocker',
        )


# @omlish-manifest
_CLI_MODULE = CliModule('docker', __name__)


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()(exit=True)
