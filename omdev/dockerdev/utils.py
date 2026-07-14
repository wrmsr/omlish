import subprocess
import sys
import typing as ta

from omcore import check


##


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
