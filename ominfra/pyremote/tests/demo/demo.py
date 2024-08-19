"""
FIXME:
 - ubuntu installs py3.10 lols
"""
import json
import os.path
import subprocess
import typing as ta
import zlib

from ominfra.deploy.tests import utils as u
from omlish import check
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

from ...bootstrap import BOOTSTRAP_ACK0
from ...bootstrap import BOOTSTRAP_ACK1
from ...bootstrap import bootstrap_payload
from ...runcommands import CommandRequest
from ...runcommands import CommandResponse


class LineReader:
    def __init__(self) -> None:
        super().__init__()
        self._buf = bytearray()

    def __call__(self, e: bytes) -> ta.Iterable[bytes]:
        self._buf += e
        while (i := self._buf.find(b'\n')) >= 0:
            yield self._buf[:i+1]
            self._buf = self._buf[i+1:]


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

        with open(os.path.join(cur_dir, '../..', '_runcommands.py')) as f:
            real_main_src = f.read()
        main_src = '\n\n'.join([
            real_main_src,
            'run_commands_main()',

        ])
        main_z = zlib.compress(main_src.encode('utf-8'))

        proc = subprocess.Popen(
            [
                'docker', 'exec', '-i', ctr_id,
                'python3', '-c', bootstrap_payload(context_name, len(main_z)),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdin = check.not_none(proc.stdin)
        stdout = check.not_none(proc.stdout)
        stderr = check.not_none(proc.stderr)

        stdin.write(main_z)
        stdin.flush()

        check.equal(stdout.read(8), BOOTSTRAP_ACK0)
        check.equal(stdout.read(8), BOOTSTRAP_ACK1)

        ##

        line_reader = LineReader()
        lines_buf = []

        def next_line() -> bytes:
            while True:
                if lines_buf:
                    return lines_buf.pop(0)
                lines_buf.extend(line_reader(stdout.read(0x4000)))

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
            l = next_line()
            resp: CommandResponse = unmarshal_obj(json.loads(l.decode('utf-8')), CommandResponse)
            print(resp)

        stdin.write(b'\n')
        stdin.flush()
        proc.wait(TIMEBOMB_DELAY_S)


if __name__ == '__main__':
    _main()
