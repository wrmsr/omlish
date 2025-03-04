# @omlish-lite
import shlex


##


_DEFAULT_DOCKER_TIMEBOMB_NAME = 'omlish-timebomb'


def docker_timebomb_payload(delay_s: float, name: str = _DEFAULT_DOCKER_TIMEBOMB_NAME) -> str:
    return (
        '('
        f'echo {shlex.quote(name)} && '
        f'sleep {delay_s:g} && '
        'sh -c \'killall5 -9 -o $PPID -o $$ ; kill 1\''
        ') &'
    )
