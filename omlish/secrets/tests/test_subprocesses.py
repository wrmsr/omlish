import fcntl
import os
import subprocess


def test_pipes():
    buf = b'hi'

    rfd, wfd = os.pipe()
    if hasattr(fcntl, 'F_SETPIPE_SZ'):
        fcntl.fcntl(wfd, fcntl.F_SETPIPE_SZ, max(len(buf), 0x1000))
    os.write(wfd, buf)
    os.close(wfd)

    ret = subprocess.run(
        ['cat', f'/dev/fd/{rfd}'],
        pass_fds=[rfd],
        stdout=subprocess.PIPE,
        check=True,
    )
    os.close(rfd)

    print(ret.stdout)
