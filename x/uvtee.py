"""
https://gist.github.com/scivision/3629a57ea6f78c1450f2b8d4e81b8a4b
"""
# import subprocess
# import io
# import sys
#
#
# def tee_subprocess(cmd: list[str]) -> tuple[int, str]:
#     """
#     Pick stdout or stderr to tee
#     Both streams at once requires threading or asyncio to avoid deadlock.
#     bufsize=1 is line buffering
#     """
#
#     with subprocess.Popen(
#             cmd,
#             stdout=subprocess.PIPE,
#             bufsize=1,
#             text=True,
#     ) as p, io.StringIO() as buf:
#         if p.stdout:
#             for line in p.stdout:
#                 print(line, end="")
#                 buf.write(line)
#         output = buf.getvalue()
#
#     return p.returncode, output
#
#
# if __name__ == '__main__':
#     cmd = [
#         sys.executable,
#         '-u',
#         '-c',
#         '\n'.join([
#             'from time import sleep',
#             'import datetime',
#             'for _ in range(10): print(datetime.datetime.now()); sleep(0.5)',
#         ]),
#     ]
#
#     rc, stdout = tee_subprocess(cmd)
#
#     if rc:
#         raise RuntimeError(f'return code {rc}')
#
#     if 'error message' in stdout:
#         raise RuntimeError('program failed')


###


"""
https://docs.python.org/3/library/pty.html
"""
import argparse
import os
import pty
import sys
import time


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest='append', action='store_true')
    parser.add_argument('-p', dest='use_python', action='store_true')
    parser.add_argument('filename', nargs='?', default='typescript')
    options = parser.parse_args()

    shell = sys.executable if options.use_python else os.environ.get('SHELL', 'sh')
    filename = options.filename
    mode = 'ab' if options.append else 'wb'

    with open(filename, mode) as script:
        def read(fd):
            data = os.read(fd, 1024)
            script.write(data)
            return data

        print('Script started, file is', filename)
        script.write(('Script started on %s\n' % time.asctime()).encode())

        pty.spawn(shell, read)

        script.write(('Script done on %s\n' % time.asctime()).encode())
        print('Script done, file is', filename)
