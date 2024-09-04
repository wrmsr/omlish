"""
https://stackoverflow.com/a/78339316

git clone --single-branch --branch=master --filter=blob:none --sparse --depth=1 https://github.com/ggerganov/llama.cpp
cd llama.cpp
git sparse-checkout set --no-cone '/*' '!/models/*'
git checkout 8f1d81a0b6f50b9bad72db0b6fcd299ad9ecd48c

git submodule status
-8f1d81a0b6f50b9bad72db0b6fcd299ad9ecd48c vendor/llama.cpp
"""
import os.path
import shutil
import subprocess
import sys
import tempfile


REPO_URL = 'https://github.com/abetlen/llama-cpp-python'

MINIMAL_SUBMODULE = True


def _main() -> None:
    tmp_dir = tempfile.mkdtemp('-omlish-llamacpp-buildwheel')

    print(tmp_dir)

    dir_name = 'llama-cpp-python'
    subprocess.check_call([
        'git', 'clone', '--depth=1', REPO_URL, dir_name,
    ], cwd=tmp_dir)
    repo_dir = os.path.join(tmp_dir, dir_name)

    if MINIMAL_SUBMODULE:
        sub_rev = subprocess.check_output([
            'git', 'submodule', 'status',
        ], cwd=repo_dir).decode().strip()[1:]
        print(sub_rev)

        sub_url = subprocess.check_output([
            'git', 'config', '--file=.gitmodules', 'submodule.vendor/llama.cpp.url',
        ], cwd=repo_dir).decode().strip()
        print(sub_url)

        sub_dir = os.path.join(repo_dir, 'vendor', 'llama.cpp')
        shutil.rmtree(sub_dir)

        """
        cd llama.cpp
        git sparse-checkout set --no-cone '/*' '!/models/*'
        git checkout 8f1d81a0b6f50b9bad72db0b6fcd299ad9ecd48c
        """
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
        ])

        raise NotImplementedError

    else:
        subprocess.check_call([
            'git', 'submodule', 'update', '--init',
        ], cwd=repo_dir)

    subprocess.check_call([
        sys.executable, '-m', 'venv', '.venv',
    ], cwd=repo_dir)
    venv_exe_file = os.path.join(repo_dir, '.venv', 'bin', 'python')

    subprocess.check_call([
        venv_exe_file, '-m', 'pip', 'install', '-e', '.[dev]', 'build', 'wheel',
    ], cwd=repo_dir)

    cuda_dir = '/usr/local/cuda-12.2/bin'
    cmake_args = [
        '-DGGML_CUDA=on',
    ]
    build_env = {
        **os.environ,
        'PATH': os.pathsep.join([cuda_dir, os.environ['PATH']]),
        'CMAKE_ARGS': ' '.join(cmake_args),
    }
    subprocess.check_call(
        [venv_exe_file, '-m', 'build', '--wheel'],
        env=build_env,
        cwd=repo_dir,
    )


if __name__ == '__main__':
    _main()
