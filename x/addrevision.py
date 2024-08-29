import logging
import os.path
import subprocess
import tarfile

import wheel.wheelfile

from omlish import check
from omlish import logs


log = logging.getLogger(__name__)


def _add_revision_to_contents(dct: dict[str, bytes], revision: str) -> bool:
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


def _add_revision_to_archive(f: str, revision: str) -> None:
    print(f)
    if f.endswith('.whl'):
        log.info('Scanning wheel %s', f)

        zis: dict = {}
        dct: dict = {}

        with wheel.wheelfile.WheelFile(f) as wf:
            for zi in wf.filelist:
                if zi.filename == wf.record_path:
                    continue
                zis[zi.filename] = zi
                dct[zi.filename] = wf.read(zi.filename)

        if _add_revision_to_contents(dct, revision):
            log.info('Repacking wheel %s', f)
            with wheel.wheelfile.WheelFile(f + '.revision.whl', 'w') as wf:
                for n, d in dct.items():
                    wf.writestr(zis[n], d)

    elif f.endswith('.tar.gz'):
        with tarfile.open(f, 'r:gz') as tf:
            for ti in tf:
                print(ti)


EXTS = ('.tar.gz', '.whl')


def _main() -> None:
    logs.configure_standard_logging('INFO')

    revision = subprocess.check_output([
        'git',
        'describe',
        '--match=NeVeRmAtCh',
        '--always',
        '--abbrev=40',
        '--dirty',
    ]).decode().strip()

    for dp, dns, fns in os.walk('dist'):
        for f in fns:
            if any(f.endswith(ext) for ext in EXTS):
                _add_revision_to_archive(os.path.join(dp, f), revision)


if __name__ == '__main__':
    _main()
