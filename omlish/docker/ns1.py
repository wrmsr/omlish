# ruff: noqa: UP006 UP007
# @omlish-lite
import typing as ta


def build_docker_ns1_run_args(
        cmd: ta.Sequence[str],
        *,
        image: str = 'debian',
        nsenter: str = 'nsenter',
) -> ta.List[str]:
    """
    - https://gist.github.com/BretFisher/5e1a0c7bcca4c735e716abf62afad389
    - https://github.com/justincormack/nsenter1/blob/8d3ba504b2c14d73c70cf34f1ec6943c093f1b02/nsenter1.c

    alt:
     - nc -U ~/Library/Containers/com.docker.docker/Data/debug-shell.sock
    """

    if isinstance(cmd, str):
        raise TypeError(cmd)

    return [
        '--privileged',
        '--pid=host',
        image,

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
