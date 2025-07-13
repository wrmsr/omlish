# @omlish-amalg ../../../scripts/journald2aws.py
import argparse
import dataclasses as dc
import os.path
import sys

from omlish.lite.configs import load_config_file_obj
from omlish.logs.standard import configure_standard_logging

from .driver import JournalctlToAwsDriver


##


def _main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('--config-file')
    parser.add_argument('-v', '--verbose', action='store_true')

    parser.add_argument('--after-cursor', nargs='?')
    parser.add_argument('--since', nargs='?')
    parser.add_argument('--dry-run', action='store_true')

    parser.add_argument('--message', nargs='?')
    parser.add_argument('--real', action='store_true')
    parser.add_argument('--num-messages', type=int)
    parser.add_argument('--runtime-limit', type=float)

    args = parser.parse_args()

    #

    configure_standard_logging('DEBUG' if args.verbose else 'INFO')

    #

    config: JournalctlToAwsDriver.Config
    if args.config_file:
        config = load_config_file_obj(
            os.path.expanduser(args.config_file),
            JournalctlToAwsDriver.Config,
        )
    else:
        config = JournalctlToAwsDriver.Config()

    #

    for k in ['aws_access_key_id', 'aws_secret_access_key']:
        if not getattr(config, k) and k.upper() in os.environ:
            config = dc.replace(config, **{k: os.environ.get(k.upper())})  # type: ignore

    #

    if not args.real:
        config = dc.replace(config, journalctl_cmd=[
            sys.executable,
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'journald', 'genmessages.py'),
            '--sleep-n', '2',
            '--sleep-s', '.5',
            *(['--message', args.message] if args.message else []),
            str(args.num_messages or 100_000),
        ])

    #

    for ca, pa in [
        ('journalctl_after_cursor', 'after_cursor'),
        ('journalctl_since', 'since'),
        ('aws_dry_run', 'dry_run'),
    ]:
        if (av := getattr(args, pa)):
            config = dc.replace(config, **{ca: av})

    #

    with JournalctlToAwsDriver(config) as jta:
        jta.run()


if __name__ == '__main__':
    _main()
