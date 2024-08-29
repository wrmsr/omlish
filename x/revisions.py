import argparse
import io
import logging
import os.path
import subprocess
import tarfile

import wheel.wheelfile

from omlish import logs


log = logging.getLogger(__name__)


def _add_rev_to_contents(dct: dict[str, bytes], revision: str) -> bool:
    changed = False
    for n in dct:
        if not n.endswith('__about__.py'):
            continue
        src = dct[n].decode('utf-8')
        lines = src.splitlines()
        for i, l in enumerate(lines):
            if l != '__revision__ = None':
                continue
            lines[i] = f"__revision__ = '{revision}'"
            changed = True
        dct[n] = '\n'.join(lines).encode('utf-8')
    return changed


def _add_rev_to_wheel(f: str, revision: str) -> None:
    log.info('Scanning wheel %s', f)

    zis: dict = {}
    dct: dict = {}
    with wheel.wheelfile.WheelFile(f) as wf:
        for zi in wf.filelist:
            if zi.filename == wf.record_path:
                continue
            zis[zi.filename] = zi
            dct[zi.filename] = wf.read(zi.filename)

    if _add_rev_to_contents(dct, revision):
        log.info('Repacking wheel %s', f)
        with wheel.wheelfile.WheelFile(f + '.revision.whl', 'w') as wf:
            for n, d in dct.items():
                wf.writestr(zis[n], d)


def _add_rev_to_tgz(f: str, revision: str) -> None:
    log.info('Scanning tgz %s', f)

    tis: dict = {}
    dct: dict = {}
    with tarfile.open(f, 'r:gz') as tf:
        for ti in tf:
            tis[ti.name] = ti
            if ti.type == tarfile.REGTYPE:
                with tf.extractfile(ti.name) as tif:
                    dct[ti.name] = tif.read()

    if _add_rev_to_contents(dct, revision):
        log.info('Repacking tgz %s', f)
        with tarfile.open(f + '.revision.tar.gz', 'w:gz') as tf:
            for n, ti in tis.items():
                log.info('Adding tarinfo %s', n)
                tf.addfile(ti, fileobj=io.BytesIO(dct[n]) if n in dct else None)


EXTS = ('.tar.gz', '.whl')


def _add_rev_to_file(f: str, revision: str) -> None:
    if f.endswith('.whl'):
        _add_rev_to_wheel(f, revision)

    elif f.endswith('.tar.gz'):
        _add_rev_to_tgz(f, revision)


#


def _get_revision() -> str:
    return subprocess.check_output([
        'git',
        'describe',
        '--match=NeVeRmAtCh',
        '--always',
        '--abbrev=40',
        '--dirty',
    ]).decode().strip()


def _add_cmd(args) -> None:
    revision = _get_revision()
    log.info('Using revision %s', revision)

    if not args.targets:
        raise Exception('must specify targets')

    for tgt in args.targets:
        if os.path.isfile(tgt):
            _add_rev_to_file(tgt)

        elif os.path.isdir(tgt):
            for dp, dns, fns in os.walk(tgt):
                for f in fns:
                    if any(f.endswith(ext) for ext in EXTS):
                        _add_rev_to_file(os.path.join(dp, f), revision)


def _main(argv=None) -> None:
    logs.configure_standard_logging('INFO')

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('targets', nargs='*')
    parser_add.set_defaults(func=_add_cmd)

    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
