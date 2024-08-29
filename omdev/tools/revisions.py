"""
TODO:
 - omlish-lite, move to pyproject/
  - vendor-lite wheel.wheelfile
"""
import argparse
import io
import logging
import os.path
import subprocess
import tarfile

import wheel.wheelfile

from omlish import logs


log = logging.getLogger(__name__)


class RevisionAdder:
    def __init__(
            self,
            revision: str,
            output_suffix: str | None = None,
    ) -> None:
        super().__init__()
        self._revision = revision
        self._output_suffix = output_suffix

    REVISION_ATTR = '__revision__'

    def add_to_contents(self, dct: dict[str, bytes]) -> bool:
        changed = False
        for n in dct:
            if not n.endswith('__about__.py'):
                continue
            src = dct[n].decode('utf-8')
            lines = src.splitlines(keepends=True)
            for i, l in enumerate(lines):
                if l != f'{self.REVISION_ATTR} = None\n':
                    continue
                lines[i] = f"{self.REVISION_ATTR} = '{self._revision}'\n"
                changed = True
            dct[n] = ''.join(lines).encode('utf-8')
        return changed

    def add_to_wheel(self, f: str) -> None:
        if not f.endswith('.whl'):
            raise Exception(f)
        log.info('Scanning wheel %s', f)

        zis: dict = {}
        dct: dict = {}
        with wheel.wheelfile.WheelFile(f) as wf:
            for zi in wf.filelist:
                if zi.filename == wf.record_path:
                    continue
                zis[zi.filename] = zi
                dct[zi.filename] = wf.read(zi.filename)

        if self.add_to_contents(dct):
            of = f[:-4] + (self._output_suffix or '') + '.whl'
            log.info('Repacking wheel %s', of)
            with wheel.wheelfile.WheelFile(of, 'w') as wf:
                for n, d in dct.items():
                    wf.writestr(zis[n], d)

    def add_to_tgz(self, f: str) -> None:
        if not f.endswith('.tar.gz'):
            raise Exception(f)
        log.info('Scanning tgz %s', f)

        tis: dict = {}
        dct: dict = {}
        with tarfile.open(f, 'r:gz') as tf:
            for ti in tf:
                tis[ti.name] = ti
                if ti.type == tarfile.REGTYPE:
                    with tf.extractfile(ti.name) as tif:  # type: ignore
                        dct[ti.name] = tif.read()

        if self.add_to_contents(dct):
            of = f[:-6] + (self._output_suffix or '') + '.tar.gz'
            log.info('Repacking tgz %s', of)
            with tarfile.open(of, 'w:gz') as tf:
                for n, ti in tis.items():
                    log.info('Adding tarinfo %s', n)
                    tf.addfile(ti, fileobj=io.BytesIO(dct[n]) if n in dct else None)

    EXTS = ('.tar.gz', '.whl')

    def add_to_file(self, f: str) -> None:
        if f.endswith('.whl'):
            self.add_to_wheel(f)

        elif f.endswith('.tar.gz'):
            self.add_to_tgz(f)

    def add_to(self, tgt: str) -> None:
        if os.path.isfile(tgt):
            self.add_to_file(tgt)

        elif os.path.isdir(tgt):
            for dp, dns, fns in os.walk(tgt):  # noqa
                for f in fns:
                    if any(f.endswith(ext) for ext in self.EXTS):
                        self.add_to_file(os.path.join(dp, f))


#


def get_revision() -> str:
    return subprocess.check_output([
        'git',
        'describe',
        '--match=NeVeRmAtCh',
        '--always',
        '--abbrev=40',
        '--dirty',
    ]).decode().strip()


#


def _add_cmd(args) -> None:
    if (revision := args.revision) is None:
        revision = get_revision()
        log.info('Using revision %s', revision)

    if not args.targets:
        raise Exception('must specify targets')

    ra = RevisionAdder(
        revision,
        output_suffix=args.suffix,
    )
    for tgt in args.targets:
        ra.add_to(tgt)


def _main(argv=None) -> None:
    logs.configure_standard_logging('INFO')

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('-r', '--revision')
    parser_add.add_argument('-s', '--suffix')
    parser_add.add_argument('targets', nargs='*')
    parser_add.set_defaults(func=_add_cmd)

    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
