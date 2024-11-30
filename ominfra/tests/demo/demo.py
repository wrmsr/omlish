"""
FIXME:
 - ubuntu installs py3.10 lols
"""
import json
import os.path
import subprocess
import typing as ta

from omlish import check
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

from ... import pyremote
from ...manage.deploy.tests import utils as u
from ..runcommands import CommandRequest
from ..runcommands import CommandResponse


class LineReader:
    def __init__(self) -> None:
        super().__init__()
        self._buf = bytearray()

    def __call__(self, e: bytes) -> ta.Iterable[bytes]:
        self._buf += e
        while (i := self._buf.find(b'\n')) >= 0:
            yield self._buf[:i + 1]
            self._buf = self._buf[i + 1:]


TIMEBOMB_DELAY_S = 20 * 60


def _main():
    img_name = 'wrmsr/omlish-pyremote-demo'
    cur_dir = os.path.dirname(__file__)
    u.build_docker_image(img_name, cur_dir)

    ssh_password = 'foobar'  # noqa

    with u.launch_docker_container(
            '-e', f'SSH_PASSWORD={ssh_password}',
            '-p', '9092:22',
            img_name,
            timebomb_delay_s=TIMEBOMB_DELAY_S,
    ) as ctr_id:  # noqa
        context_name = f'docker:{ctr_id}'

        with open(os.path.join(cur_dir, '..', '_runcommands.py')) as f:
            real_main_src = f.read()

        main_src = '\n\n'.join([
            real_main_src,
            'run_commands_main()',
        ])

        proc = subprocess.Popen(
            [
                'docker', 'exec', '-i', ctr_id,
                'python3', '-c', pyremote.pyremote_build_bootstrap_cmd(context_name),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdin = check.not_none(proc.stdin)
        stdout = check.not_none(proc.stdout)
        stderr = check.not_none(proc.stderr)  # noqa

        ##

        gen = pyremote.PyremoteBootstrapDriver(main_src)()
        gi: bytes | None = None
        while True:
            try:
                if gi is not None:
                    go = gen.send(gi)
                else:
                    go = next(gen)
            except StopIteration as e:
                br = e.value
                break
            if isinstance(go, pyremote.PyremoteBootstrapDriver.Read):
                gi = stdout.read(go.sz)
            elif isinstance(go, pyremote.PyremoteBootstrapDriver.Write):
                gi = None
                stdin.write(go.d)
                stdin.flush()
            else:
                raise TypeError(go)

        print(f'{br=}')

        ##

        line_reader = LineReader()
        lines_buf: list[bytes] = []

        def next_line() -> bytes:
            while True:
                if lines_buf:
                    return lines_buf.pop(0)
                print('read1')
                buf = stdout.read1(0x4000)  # type: ignore
                print(f'read1: {buf}')
                lines_buf.extend(line_reader(buf))

        ##

        reqs = [
            CommandRequest(cmd=['echo', 'hi']),
            CommandRequest(cmd=['uptime']),
            CommandRequest(cmd=['false']),
        ]
        for req in reqs:
            stdin.write(json_dumps_compact(marshal_obj(req)).encode('utf-8'))
            stdin.write(b'\n')
            stdin.flush()

            # l = stdin.readline()
            l = next_line()

            resp: CommandResponse = unmarshal_obj(json.loads(l.decode('utf-8')), CommandResponse)
            print(resp)

        stdin.write(b'\n')
        stdin.flush()
        proc.wait(TIMEBOMB_DELAY_S)


if __name__ == '__main__':
    _main()
