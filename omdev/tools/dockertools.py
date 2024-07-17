import os
import shutil
import subprocess

from omlish import argparse as ap
from omlish import check
from omlish import lang
from omlish import logs


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
    @ap.command(
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

    @ap.command(
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


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
