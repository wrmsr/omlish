"""
#!/usr/bin/env bash
set -ex

DST=nn
SRC=tinygrad

if [ -e $DST/nn ] ; then rm -rf $DST/nn ; fi

cp -rv $SRC/tinygrad/* $DST/nn/
cp $SRC/test/*.py $DST/nn/tests/
cp $SRC/extra/*.py $DST/nn/extra/
cp -rv $SRC/extra/datasets $DST/nn/extra/
cp $SRC/extra/models/*.py $DST/nn/extra/models/
cp $SRC/extra/optimization/*.py $DST/nn/extra/optimization/
cp -rv $SRC/test/models/* $DST/nn/extra/models/tests/
"""
import glob
import os.path
import pathlib
import shutil
import subprocess
import sys

from omlish import check
from rope.base.pyobjectsdef import PyModule
import rope.base.libutils
import rope.base.project
import rope.refactor.importutils
import rope.refactor.move
import rope.refactor.rename


def _main() -> None:
    src_path = pathlib.Path(os.path.expanduser('~/src/geohot/tinygrad'))
    dst_path = pathlib.Path(os.path.expanduser('~/src/wrmsr/omlish/x/roper/nn'))

    if dst_path.exists():
        shutil.rmtree(dst_path)
    os.mkdir(dst_path)
    os.mkdir(dst_path / 'nn')

    for f in glob.glob(str(src_path / 'tinygrad/*.py')):
        shutil.copy(f, dst_path / 'nn' / os.path.basename(f))

    os.chdir(str(dst_path))

    subprocess.Popen([
        sys.executable,
        '-m', 'black',
        str(dst_path),
    ]).communicate()

    refac_path = 'nn/tensor.py'

    project = rope.base.project.Project('.', ropefolder='.clirope')

    resource = project.get_resource(refac_path)
    pymodule = check.isinstance(project.get_pymodule(resource), PyModule)
    project.validate(resource)

    tools = rope.refactor.importutils.ImportTools(project)
    new_content = tools.froms_to_imports(pymodule)

    pathlib.Path(refac_path).write_text(new_content)


if __name__ == '__main__':
    _main()
