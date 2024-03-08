"""
TODO:
 - vendor
  - pip index versions antlr4-python3-runtime -> "antlr4-python3-runtime (4.13.1)"
  - pip download antlr4-python3-runtime==4.13.1
  - unzip *.whl
  - https://github.com/antlr/antlr4/raw/4.13.1/LICENSE.txt
  - ... antlr4 ...
"""
import concurrent.futures as cf
import contextlib
import logging
import os.path
import subprocess
import shutil
import sys
import re
import typing as ta

from omlish import argparse as ap
from omlish import asyncs
from omlish import lang
from omlish import logs
from omlish import cached


log = logging.getLogger(__name__)


ANTLR_VERSION = '4.13.1'

ANTLR_RUNTIME_PACKAGE = 'antlr4-python3-runtime'
ANTLR_GITHUB_REPO = 'antlr/antlr4'


def _build():
    pass


def _find_dirs(base_path: str, predicate: ta.Callable[[str], bool] = lambda _: True) -> ta.Sequence[str]:
    return sorted(
        os.path.join(dp, dn)
        for dp, dns, fns in os.walk(base_path)
        for dn in dns
        if predicate(dn)
    )


def _find_files(base_path: str, predicate: ta.Callable[[str], bool] = lambda _: True) -> ta.Sequence[str]:
    return sorted(
        os.path.join(dp, fn)
        for dp, dns, fns in os.walk(base_path)
        for fn in fns
        if predicate(fn)
    )


class Cli(ap.Cli):

    @cached.property
    def work_path(self) -> str:
        return os.getcwd()

    @lang.cached_nullary
    def get_antlr_jar_path(self) -> str:
        fn = f'antlr-{ANTLR_VERSION}-complete.jar'
        fp = os.path.join(self.work_path, fn)
        if not os.path.exists(fp):
            subprocess.check_call([
                'curl',
                '--proto', '=https',
                '--tlsv1.2',
                f'https://www.antlr.org/download/antlr-{ANTLR_VERSION}-complete.jar',
                '-o', fp,
            ])
        return os.path.abspath(fp)

    @ap.command(
        ap.arg('base_path', metavar='base-path'),
        ap.arg('--self-vendor', dest='self_vendor', action='store_true'),
    )
    def gen(self) -> None:
        dns = _find_dirs(self.args.base_path, lambda dn: os.path.basename(dn) == '_antlr')
        for dn in dns:
            shutil.rmtree(dn)

        fns = _find_files(self.args.base_path, lambda fn: fn.endswith('.g4'))
        aps = set()
        for fn in fns:
            dp = os.path.dirname(fn)

            ap = os.path.join(dp, '_antlr')
            if not os.path.exists(ap):
                os.mkdir(ap)

            shutil.copy(fn, ap)
            aps.add(ap)

        wps = set()
        for ap in sorted(aps):
            fns = [fn for fn in os.listdir(ap) if fn.endswith('.g4')]
            for fn in fns:
                fp = os.path.join(ap, fn)
                wps.add(fp)

        def process_g4(fp: str) -> None:
            ap = os.path.dirname(fp)
            fn = os.path.basename(fp)
            log.info(f'Compiling grammar {fp}')

            try:
                subprocess.check_call([
                    'java',
                    '-jar', self.get_antlr_jar_path(),
                    '-Dlanguage=Python3',
                    '-visitor',
                    os.path.basename(fn),
                ], cwd=ap)
            except Exception as e:  # noqa
                log.exception(f'Exception in grammar {fp}')

        parallelism = 4
        with contextlib.ExitStack() as es:
            if parallelism is not None and parallelism > 0:
                exe = es.enter_context(cf.ThreadPoolExecutor(parallelism))
            else:
                exe = asyncs.ImmediateExecutor()

            futs = [exe.submit(process_g4, fp) for fp in sorted(wps)]
            asyncs.await_futures(futs, raise_exceptions=True, timeout_s=60 * 60)

        for ap in sorted(aps):
            fns = [fn for fn in os.listdir(ap) if not fn.endswith('.py')]
            for fn in fns:
                fp = os.path.join(ap, fn)
                os.unlink(fp)

            init_lines = []
            fns = [fn for fn in os.listdir(ap) if fn.endswith('.py') and fn != '__init__.py']
            for fn in fns:
                if self.args.self_vendor:
                    pkg_depth = len(os.path.normpath(ap).split(os.path.sep))
                    antlr_imp = f'from {"." * pkg_depth}_vendor.antlr4'
                else:
                    antlr_imp = f'from {__package__.split(".")[0]}._vendor.antlr4'

                def fix(l: str) -> str:
                    return re.sub(r'^from antlr4', antlr_imp, l)

                fp = os.path.join(ap, fn)
                with open(fp, 'r') as f:
                    lines = f.readlines()

                lines = [
                    '# flake8: noqa\n',
                    '# type: ignore\n',
                ] + [fix(l) for l in lines]

                for l in lines:
                    m = re.match(r'^class (?P<cn>[A-Za-z0-9_]+)', l)
                    if m is not None:
                        fcn = fn.split('.')[0]
                        init_lines.append(f'from .{fcn} import {m.groupdict()["cn"]}  # noqa')

                with open(fp, 'w') as f:
                    f.write(''.join(lines).strip())
                    f.write('\n')

            ip = os.path.join(ap, '__init__.py')
            with open(ip, 'w') as f:
                f.write('\n'.join(sorted(init_lines)))
                f.write('\n')

    @ap.command()
    def latest(self) -> None:
        o, _ = subprocess.Popen(
            [
                sys.executable,
                '-m', 'pip',
                'index', 'versions',
                ANTLR_RUNTIME_PACKAGE,
            ],
            stdout=subprocess.PIPE,
        ).communicate()
        tl = o.decode().splitlines()[0]
        m = re.fullmatch(rf'{ANTLR_RUNTIME_PACKAGE} \((?P<version>[^)]+)\)', tl)
        v = m.groupdict()['version']
        print(v)


def main():
    logs.configure_standard_logging(logging.INFO)
    cli = Cli()
    cli()


if __name__ == '__main__':
    main()
