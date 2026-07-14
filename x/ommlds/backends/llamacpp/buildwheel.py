#!/usr/bin/env python3
# @omlish-script
"""
https://stackoverflow.com/a/78339316

TODO:
 - cmake .. -DLLAMA_CURL=1

git clone --single-branch --branch=master --filter=blob:none --sparse --depth=1 https://github.com/ggerganov/llama.cpp
cd llama.cpp
git sparse-checkout set --no-cone '/*' '!/models/*'
git checkout 8f1d81a0b6f50b9bad72db0b6fcd299ad9ecd48c

git submodule status
-8f1d81a0b6f50b9bad72db0b6fcd299ad9ecd48c vendor/llama.cpp
"""
import glob
import os.path
import shutil
import subprocess
import sys
import tempfile


##


REPO_URL = 'https://github.com/abetlen/llama-cpp-python'

REV: str | None = None
# REV = 'v0.2.90'
# REV = '077ecb6771fbd373d5507444f6e0b6e9bb7cf4e8'

MINIMAL_SUBMODULE = True


def _main() -> None:
    tmp_dir = tempfile.mkdtemp(f'-om-llamacpp-buildwheel')

    print(tmp_dir)

    #

    dir_name = 'llama-cpp-python'

    subprocess.check_call([
        'git', 'clone', '--depth=1', REPO_URL, dir_name,
    ], cwd=tmp_dir)
    repo_dir = os.path.join(tmp_dir, dir_name)

    if REV is not None:
        subprocess.check_call([
            'git', 'fetch', '--tags', 'origin', REV,
        ], cwd=repo_dir)
        subprocess.check_call([
            'git', 'checkout', REV,
        ], cwd=repo_dir)

    #

    if MINIMAL_SUBMODULE:
        sub_rev = subprocess.check_output([
            'git', 'submodule', 'status',
        ], cwd=repo_dir).decode().strip()[1:].split()[0]
        print(sub_rev)

        sub_url = subprocess.check_output([
            'git',
            'config',
            '--file=.gitmodules',
            'submodule.vendor/llama.cpp.url',
        ], cwd=repo_dir).decode().strip()
        print(sub_url)

        vendor_dir = os.path.join(repo_dir, 'vendor')
        sub_dir = os.path.join(vendor_dir, 'llama.cpp')
        shutil.rmtree(sub_dir)

        subprocess.check_call([
            'git',
            'clone',
            '--single-branch',
            '--branch=master',
            '--filter=blob:none',
            '--sparse',
            '--depth=1',
            sub_url,
            'llama.cpp',
        ], cwd=vendor_dir)

        subprocess.check_call([
            'git',
            'sparse-checkout',
            'set',
            '--no-cone',
            '/*',
            # '!/examples/*',
            '!/models/*',
        ], cwd=sub_dir)

        subprocess.check_call([
            'git', 'checkout', sub_rev,
        ], cwd=sub_dir)

        os.unlink(os.path.join(repo_dir, '.gitmodules'))

    else:
        subprocess.check_call([
            'git', 'submodule', 'update', '--init',
        ], cwd=repo_dir)

    #

    subprocess.check_call([
        sys.executable, '-m', 'venv', '.venv',
    ], cwd=repo_dir)
    venv_exe_file = os.path.join(repo_dir, '.venv', 'bin', 'python')

    subprocess.check_call([
        venv_exe_file, '-m', 'pip', 'install', 'build', 'wheel',
    ], cwd=repo_dir)

    subprocess.check_call([
        venv_exe_file, '-m', 'pip', 'install', '-e', '.[dev]',
    ], cwd=repo_dir)

    #

    path_items: list[str] = []
    cmake_args: list[str] = []

    if sys.platform == 'linux':
        cuda_dir = os.path.join(os.path.realpath('/usr/local/cuda'), 'bin')
        path_items.append(cuda_dir)
        cmake_args.append('-DGGML_CUDA=on')

    elif sys.platform == 'darwin':
        cmake_args.append('-DGGML_METAL=on')

    build_env = {
        **os.environ,
        'PATH': os.pathsep.join([*path_items, os.environ['PATH']]),
        'CMAKE_ARGS': ' '.join(cmake_args),
    }

    subprocess.check_call(
        [venv_exe_file, '-m', 'build', '--wheel'],
        env=build_env,
        cwd=repo_dir,
    )

    #

    dist_dir = os.path.join(repo_dir, 'dist')
    whl_files = glob.glob(os.path.join(dist_dir, '*.whl'))
    print('\n'.join(whl_files))


if __name__ == '__main__':
    _main()
