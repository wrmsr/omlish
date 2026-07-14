# ruff: noqa: UP006 UP007 UP045
"""
https://docs.python.org/3/library/unittest.html#command-line-interface
~ https://github.com/python/cpython/tree/f66c75f11d3aeeb614600251fd5d3fe1a34b5ff1/Lib/unittest

TODO:
 - giving it filenames doesn't work
"""
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001-2024 Python Software Foundation; All Rights
# Reserved" are retained in Python alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
import argparse
import dataclasses as dc
import importlib.util
import os
import re
import sys
import types
import typing as ta

from .loading import UnittestTargetLoader
from .running import UnittestTestRunner


##


class UnittestRunCli:
    def __init__(self) -> None:
        super().__init__()

        self._parser = self._get_arg_parser()

    #

    DEFAULT_DISCOVERY_START = '.'
    DEFAULT_DISCOVERY_PATTERN = 'test*.py'

    def _get_arg_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument(
            '-v',
            '--verbose',
            dest='verbosity',
            action='store_const',
            const=2,
            help='Verbose output',
        )

        parser.add_argument(
            '-q',
            '--quiet',
            dest='verbosity',
            action='store_const',
            const=0,
            help='Quiet output',
        )

        parser.add_argument(
            '--locals',
            dest='tb_locals',
            action='store_true',
            help='Show local variables in tracebacks',
        )

        parser.add_argument(
            '-f',
            '--failfast',
            dest='failfast',
            action='store_true',
            help='Stop on first fail or error',
        )

        parser.add_argument(
            '-c',
            '--catch',
            dest='catchbreak',
            action='store_true',
            help='Catch Ctrl-C and display results so far',
        )

        parser.add_argument(
            '-b',
            '--buffer',
            dest='buffer',
            action='store_true',
            help='Buffer stdout and stderr during tests',
        )

        def _convert_select_pattern(pattern: str) -> str:
            if '*' not in pattern:
                pattern = f'*{pattern}*'
            return pattern

        parser.add_argument(
            '-k',
            dest='test_name_patterns',
            action='append',
            type=_convert_select_pattern,
            help='Only run tests which match the given substring',
        )

        #

        parser.epilog = (
            'For test discovery all test modules must be importable from the top level directory of the project.'
        )

        parser.add_argument(
            '-s',
            '--start-directory',
            default=self.DEFAULT_DISCOVERY_START,
            dest='start',
            help="Directory to start discovery ('.' default)",
        )

        parser.add_argument(
            '-p',
            '--pattern',
            default=self.DEFAULT_DISCOVERY_PATTERN,
            dest='pattern',
            help="Pattern to match tests ('test*.py' default)",
        )

        parser.add_argument(
            '-t',
            '--top-level-directory',
            dest='top',
            help='Top level directory of project (defaults to start directory)',
        )

        parser.add_argument(
            'target',
            nargs='*',
            default=argparse.SUPPRESS,
            help=argparse.SUPPRESS,
        )

        return parser

    #

    @dc.dataclass(frozen=True)
    class ParsedArgs:
        args: ta.Optional[argparse.Namespace]
        test_names: ta.Optional[ta.Sequence[str]] = None
        module: ta.Union[str, types.ModuleType, None] = None

    def parse_args(self, argv: ta.Sequence[str]) -> ParsedArgs:
        args = self._parser.parse_args(argv)
        return self.ParsedArgs(args)

    #

    @staticmethod
    def _get_attr_dict(obj: ta.Optional[ta.Any], *attrs: str) -> ta.Dict[str, ta.Any]:
        if obj is None:
            return {}

        return {
            a: v
            for a in attrs
            if (v := getattr(obj, a, None)) is not None
        }

    #

    IMPORT_PATH_PAT = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*')

    def _build_target(self, name: str, args: ParsedArgs) -> UnittestTargetLoader.Target:
        is_discovery = False
        if os.path.isdir(name):
            is_discovery = True
        elif self.IMPORT_PATH_PAT.fullmatch(name):
            spec = importlib.util.find_spec(name)
            if spec is not None and spec.submodule_search_locations is not None:  # is a package, not a module
                is_discovery = True

        if not is_discovery:
            return UnittestTargetLoader.NamesTarget([name])

        else:
            return UnittestTargetLoader.DiscoveryTarget(
                start=name,
                **self._get_attr_dict(
                    args.args,
                    'pattern',
                    'top',
                ),
            )

    #

    NO_TESTS_EXITCODE = 5

    def run(
            self,
            args: ParsedArgs,
            *,
            exit: bool = False,  # noqa
    ) -> None:
        loader = UnittestTargetLoader(**self._get_attr_dict(
            args.args,
            'test_name_patterns',
        ))

        tests = [
            loader.load(self._build_target(target_arg, args))
            for target_arg in (args.args.target if args.args is not None else None) or []  # noqa
        ]

        runner = UnittestTestRunner(UnittestTestRunner.Args(**self._get_attr_dict(
            args.args,
            'verbosity',
            'failfast',
            'catchbreak',
            'buffer',
            'warnings',
            'tb_locals',
        )))

        result = runner.run_many(tests)

        runner.print(result)

        if exit:
            if not result.num_tests_run and not result.skipped:
                raise SystemExit(self.NO_TESTS_EXITCODE)
            elif result.was_successful:
                raise SystemExit(0)
            else:
                raise SystemExit(1)


##


def _main() -> None:
    cli = UnittestRunCli()
    args = cli.parse_args(sys.argv[1:])
    cli.run(args, exit=True)


if __name__ == '__main__':
    _main()
