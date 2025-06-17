# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import re
import typing as ta

from ..lite.check import check
from ..subprocesses.run import SubprocessRun
from ..subprocesses.run import SubprocessRunnable
from ..subprocesses.run import SubprocessRunOutput


##


DEFAULT_DOCKER_NS1_RUN_IMAGE: str = 'debian'


def build_docker_ns1_run_args(
        *cmd: str,
        image: ta.Optional[str] = None,
        nsenter: str = 'nsenter',
) -> ta.List[str]:
    """
    - https://gist.github.com/BretFisher/5e1a0c7bcca4c735e716abf62afad389
    - https://github.com/justincormack/nsenter1/blob/8d3ba504b2c14d73c70cf34f1ec6943c093f1b02/nsenter1.c

    alt:
     - nc -U ~/Library/Containers/com.docker.docker/Data/debug-shell.sock
    """

    return [
        '--privileged',
        '--pid=host',
        (image if image is not None else DEFAULT_DOCKER_NS1_RUN_IMAGE),

        nsenter,
        '-t', '1',

        '-m',  # mount
        '-u',  # uts
        '-i',  # ipc
        '-n',  # net
        '-p',  # pid
        '-C',  # cgroup
        # '-U',  # user
        '-T',  # time

        *cmd,
    ]


def build_docker_ns1_run_cmd(
        *cmd: str,
        exe: str = 'docker',
        run_args: ta.Optional[ta.Sequence[str]] = None,
        **kwargs: ta.Any,
) -> ta.List[str]:
    if run_args is not None:
        check.not_isinstance(run_args, str)

    return [
        exe,
        'run',
        '--rm',
        *(run_args if run_args is not None else []),
        '-i',
        *build_docker_ns1_run_args(*cmd, **kwargs),
    ]


##


@dc.dataclass(frozen=True)
class DockerNs1ListUsedTcpPortsCommand(SubprocessRunnable[ta.List[int]]):
    kwargs: ta.Optional[ta.Mapping[str, str]] = None

    def make_run(self) -> SubprocessRun:
        return SubprocessRun.of(
            *build_docker_ns1_run_cmd(
                'netstat', '-tan',
            ),
            stdout='pipe',
            stderr='devnull',
            check=True,
        )

    _NETSTAT_LINE_PAT: ta.ClassVar[re.Pattern] = re.compile(r'\d{1,3}(.(\d{1,3})){3}:(?P<port>\d+)')

    def handle_run_output(self, output: SubprocessRunOutput) -> ta.List[int]:
        lines = [s for l in check.not_none(output.stdout).decode().splitlines() if (s := l.strip())]
        return [
            int(m.groupdict()['port'])
            for l in lines
            if len(ps := l.split(maxsplit=4)) > 3
            if (m := self._NETSTAT_LINE_PAT.fullmatch(ps[3])) is not None
        ]
