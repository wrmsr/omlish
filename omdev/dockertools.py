import os
import shutil

from omlish import argparse as ap
from omlish import check
from omlish import logs


class Cli(ap.Cli):
    @ap.command(
        ap.arg('args', nargs='*'),
    )
    def ns1(self):
        """
        - https://gist.github.com/BretFisher/5e1a0c7bcca4c735e716abf62afad389
        - https://github.com/justincormack/nsenter1/blob/8d3ba504b2c14d73c70cf34f1ec6943c093f1b02/nsenter1.c
        """
        exe = check.not_none(shutil.which('docker'))
        os.execl(
            exe,
            exe,
            'run',
            '-it',
            '--privileged',
            '--pid=host',
            'debian',
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


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
