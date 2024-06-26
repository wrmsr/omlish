import itertools
import os.path
import subprocess
import sysconfig
import typing as ta

from omlish import lang


ANTLR_REPO_URL = 'https://github.com/antlr/antlr4'
ANTLR_VERSION = '4.13.1'

PYBIND_REPO_URL = 'https://github.com/pybind/pybind11'
PYBIND_VERSION = '2.11.1'

# PYBIND_REPO_URL = 'https://github.com/google/pybind11k'  # TODO


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


def _find_dirs(
        base_path: str,
        predicate: ta.Callable[[str], bool] = lambda _: True,
) -> ta.Sequence[str]:
    return sorted(
        os.path.join(dp, dn)
        for dp, dns, fns in os.walk(base_path)
        for dn in dns
        if predicate(dn)
    )


def _find_files(
        base_path: str,
        predicate: ta.Callable[[str], bool] = lambda _: True,
) -> ta.Sequence[str]:
    return sorted(
        os.path.join(dp, fn)
        for dp, dns, fns in os.walk(base_path)
        for fn in fns
        if predicate(fn)
    )


class Builder:

    @lang.cached_function
    def build_dir(self) -> str:
        return os.path.join(os.path.dirname(__file__), 'build')

    @lang.cached_function
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

    def process_g4(self, g4_path: str, dir_name: str) -> None:
        d = os.path.join(self.build_dir(), dir_name)
        if not os.path.exists(d):
            subprocess.check_call(
                [
                    'java',
                    '-jar', self.antlr_jar_path(),
                    '-Dlanguage=Cpp',
                    '-visitor',
                    '-o', d,
                    g4_path,
                ],
            )

    @lang.cached_function
    def runtime_dir(self) -> str:
        d = os.path.join(self.build_dir(), 'antlr4')
        if not os.path.exists(d):
            _git_clone_subtree(
                base_dir=self.build_dir(),
                repo_url=ANTLR_REPO_URL,
                branch_name=ANTLR_VERSION,
                repo_dir='antlr4',
                repo_subtree='runtime/Cpp/runtime/src',
            )
        return d

    @lang.cached_function
    def pybind_dir(self) -> str:
        d = os.path.join(self.build_dir(), 'pybind11')
        if not os.path.exists(d):
            _git_clone_subtree(
                base_dir=self.build_dir(),
                repo_url=PYBIND_REPO_URL,
                branch_name=f'v{PYBIND_VERSION}',
                repo_dir='pybind11',
                repo_subtree='include',
            )
        return d


def _compile_src_file(
        src_file: str,
        inc_dirs: ta.Sequence[str] = (),
) -> str:
    obj_file = os.path.join(os.path.dirname(src_file), src_file.rpartition('.')[0] + '.o')
    if not os.path.exists(obj_file):
        subprocess.check_call(
            [
                'clang++',
                # '-O3',
                # '-Wall',
                '-c', os.path.basename(src_file),
                *itertools.chain.from_iterable(('-I', inc_dir) for inc_dir in inc_dirs),
                '-std=c++17',
            ],
            cwd=os.path.dirname(src_file),
        )
    return obj_file


def _compile_src_dir(
        src_dir: str,
        inc_dirs: ta.Sequence[str] = (),
        file_ext: str = '.cpp',
) -> ta.Sequence[str]:
    obj_files = []
    rt_src_files = _find_files(src_dir, lambda fn: fn.endswith(file_ext))
    for src_file in rt_src_files:
        obj_files.append(_compile_src_file(src_file, [src_dir, *inc_dirs]))
    return obj_files


def _main() -> None:
    builder = Builder()

    if not os.path.exists(build_dir := builder.build_dir()):
        os.mkdir(build_dir)

    builder.runtime_dir()
    builder.pybind_dir()

    builder.process_g4('Chat.g4', 'Chat')

    obj_files = []

    rt_src_dir = os.path.abspath(os.path.join(builder.build_dir(), 'antlr4/runtime/Cpp/runtime/src'))
    obj_files.extend(_compile_src_dir(rt_src_dir))

    pb_inc_dir = os.path.abspath(os.path.join(builder.pybind_dir(), 'include'))

    prs_src_dir = os.path.abspath(os.path.join(builder.build_dir(), 'Chat'))
    obj_files.extend(_compile_src_dir(prs_src_dir, [rt_src_dir]))

    py_inc_dir = sysconfig.get_paths()['include']

    inc_dirs = [
        rt_src_dir,
        pb_inc_dir,
        prs_src_dir,
        py_inc_dir,
    ]
    src_file = os.path.join(os.path.dirname(builder.build_dir()), 'chat.cc')
    obj_file = os.path.join(builder.build_dir(), os.path.basename(src_file).rpartition('.')[0] + '.o')
    obj_files.append(obj_file)
    subprocess.check_call(
        [
            'clang++',
            '-c', os.path.basename(src_file),
            *itertools.chain.from_iterable(('-I', inc_dir) for inc_dir in inc_dirs),
            '-std=c++17',
            '-o', obj_file,
        ],
        cwd=os.path.dirname(src_file),
    )

    bin_dir = os.path.join(builder.build_dir(), 'bin')
    if not os.path.exists(bin_dir):
        os.mkdir(bin_dir)
    subprocess.check_call(
        [
            'clang++',
            '-std=c++17',
            '-fPIC',
            '-shared',
            '-undefined', 'dynamic_lookup',
            '-Wl,-no_fixup_chains',
            *obj_files,
            '-o', os.path.join(bin_dir, 'chat.so'),
        ],
    )


if __name__ == '__main__':
    _main()
