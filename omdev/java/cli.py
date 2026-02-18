"""
TODO:
 - JAVA_HOME

See:
 - https://github.com/jbangdev/jbang
 - https://docs.oracle.com/en/java/javase/17/docs/specs/man/java.html#using-source-file-mode-to-launch-single-file-source-code-programs
"""  # noqa
import os.path
import re
import shutil
import subprocess
import tempfile
import typing as ta

from omlish import check
from omlish.argparse import all as ap

from .. import magic
from . import pomgen as pg


##


PACKAGE_PAT = re.compile(r'package\s+(\S+);\s*')

DEFAULT_PROJECT_GROUP_ID = 'tmp'
DEFAULT_PROJECT_VERSION = '0.0.1-SNAPSHOT'

DEFAULT_JAVA_VERSION = '17'


def scan_jdeps(src: str) -> ta.Sequence[str]:
    src_magics = magic.find_magic(  # noqa
        magic.C_MAGIC_STYLE,
        src.splitlines(),
        preparer=magic.json_magic_preparer,
    )

    deps: list[str] = []

    for src_magic in src_magics:
        if src_magic.key == '@omlish-jdeps':
            for dep in check.isinstance(src_magic.prepared, ta.Sequence):  # noqa
                deps.append(dep)  # noqa

    return deps


def build_maven_project(
        root_dir: str,
        src_file: str,
        *,
        deps: ta.Sequence[str] | None = None,
) -> pg.Project:
    with open(src_file) as f:
        src = f.read()

    #

    name = os.path.basename(src_file).split('.', maxsplit=1)[0]

    if (pms := list(filter(None, map(PACKAGE_PAT.fullmatch, src.splitlines())))):
        group_id = pms[0].group(1)
    else:
        group_id = DEFAULT_PROJECT_GROUP_ID
        src = f'package {group_id};\n\n{src}'

    check.non_empty_str(group_id)
    group_id_parts = group_id.split('.')
    for gi_part in group_id_parts:
        check.non_empty_str(gi_part)
        check.arg(gi_part.isalnum())

    #

    if deps is None:
        deps = scan_jdeps(src)

    #

    pom_prj = pg.Project(
        group_id,
        name,
        DEFAULT_PROJECT_VERSION,

        name,

        properties={
            'maven.compiler.source': DEFAULT_JAVA_VERSION,
            'maven.compiler.target': DEFAULT_JAVA_VERSION,
        },

        dependencies=[
            pg.Dependency(*dep.split(':'))
            for dep in deps
        ],
    )

    pom_xml = pg.render_project_xml(pom_prj)

    #

    smj_dir = os.path.join(root_dir, 'src', 'main', 'java')
    sp_dir = smj_dir
    for gi_part in group_id_parts:
        sp_dir = os.path.join(sp_dir, gi_part)
    os.makedirs(sp_dir)

    with open(os.path.join(sp_dir, os.path.basename(src_file)), 'w') as f:
        f.write(src)

    with open(os.path.join(root_dir, 'pom.xml'), 'w') as f:
        f.write(pom_xml)

    #

    return pom_prj


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('--cwd'),
        ap.arg('--java'),
        ap.arg('src-file'),
        ap.arg('args', nargs=ap.REMAINDER),
    )
    def run(self) -> int:
        src_file = self.args.src_file

        #

        with open(src_file) as f:
            src = f.read()

        #

        deps = scan_jdeps(src)

        #

        if not deps:
            proc = subprocess.run(
                [
                    self.args.java or 'java',
                    src_file,
                    *self.args.args,
                ],
                cwd=self.args.cwd,
                check=False,
            )

            return proc.returncode

        #

        tmp_dir = tempfile.mkdtemp()
        try:
            pom_prj = build_maven_project(
                tmp_dir,
                src_file,
                deps=deps,
            )

            proc = subprocess.run(
                [
                    'mvn',
                    '-q',
                    'compile',
                ],
                cwd=tmp_dir,
                check=False,
            )

            if rc := proc.returncode:
                return rc

            cp_out = subprocess.check_output(
                [
                    'mvn',
                    '-q',
                    'dependency:build-classpath',
                    '-Dmdep.includeScope=runtime',
                    '-Dmdep.outputFile=/dev/stdout',
                ],
                cwd=tmp_dir,
            )

            cp = os.path.join(tmp_dir, 'target/classes')

            if cp_out:
                cp += ':' + cp_out.decode().strip()

            proc = subprocess.run(
                [
                    self.args.java or 'java',
                    '-cp',
                    cp,
                    f'{pom_prj.group_id}.{pom_prj.name}',
                    *self.args.args,
                ],
                cwd=self.args.cwd,
                check=False,
            )

            return proc.returncode

        finally:
            shutil.rmtree(tmp_dir)

        return proc.returncode  # type: ignore[unreachable]  # noqa


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
