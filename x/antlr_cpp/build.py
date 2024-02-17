# git clone -n --depth=1 --filter=tree:0 -b 4.13.1 --single-branch https://github.com/antlr/antlr4
# cd antlr4
# git sparse-checkout set --no-cone runtime/Cpp/runtime/src
# git checkout

import os.path
import subprocess

from omlish import cached


ANTLR_VERSION = '4.13.1'
PYBIND_VERSION='2.11.1'


def _git_clone_subtree(
        *,
        base_dir: str,
        repo_url: str,
        branch_name: str,
        repo_dir: str,
        repo_subtree: str,
) -> None:
    subprocess.check_call(
        [
            'git',
            'clone',
            '-n',
            '--depth=1',
            '--filter=tree:0',
            '-b', branch_name,
            '--single-branch',
            '-o', repo_dir,
            repo_url,
        ],
        cwd=base_dir,
    )

    rd = os.path.join(base_dir, repo_dir)
    subprocess.check_call(
        [
            'git',
            'sparse-checkout',
            'set',
            '--no-cone',
            repo_subtree,
        ],
        cwd=rd,
    )
    subprocess.check_call(['git', 'checkout'], cwd=rd)


class Builder:

    @cached.nullary
    def build_dir(self) -> str:
        return os.path.join(os.path.dirname(__file__), 'build')

    @cached.nullary
    def antlr_jar_path(self) -> str:
        fn = f'antlr-{ANTLR_VERSION}-complete.jar'
        fp = os.path.abspath(os.path.join(self.build_dir(), fn))
        if not os.path.exists(fp):
            subprocess.check_call([
                'curl',
                '--proto', '=https',
                '--tlsv1.2',
                f'https://www.antlr.org/download/antlr-{ANTLR_VERSION}-complete.jar',
                '-o', fp,
            ])
        return fp

    @cached.nullary
    def runtime_dir(self) -> str:
        d = os.path.join(self.build_dir(), 'antlr4')
        if not os.path.exists(d):
            _git_clone_subtree(
                base_dir=self.build_dir(),
                repo_url='https://github.com/antlr/antlr4',
                branch_name=ANTLR_VERSION,
                repo_dir='antlr4',
                repo_subtree='runtime/Cpp/runtime/src',
            )
        return d

    @cached.nullary
    def pybind_dir(self) -> str:
        d = os.path.join(self.build_dir(), 'pybind11')
        if not os.path.exists(d):
            _git_clone_subtree(
                base_dir=self.build_dir(),
                repo_url='https://github.com/pybind/pybind11',
                branch_name=f'v{PYBIND_VERSION}',
                repo_dir='pybind11',
                repo_subtree='include',
            )
        return d


def _main() -> None:
    builder = Builder()
    builder.antlr_jar_path()
    print(builder.runtime_dir())
    print(builder.pybind_dir())


if __name__ == '__main__':
    _main()
