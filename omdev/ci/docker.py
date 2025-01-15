# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - some less stupid Dockerfile hash
  - doesn't change too much though
"""
import contextlib
import dataclasses as dc
import json
import os.path
import shlex
import tarfile
import typing as ta

from omlish.lite.check import check
from omlish.lite.contextmanagers import defer
from omlish.subprocesses import subprocesses

from .shell import ShellCmd
from .utils import make_temp_file
from .utils import sha256_str


##


def build_docker_file_hash(docker_file: str) -> str:
    with open(docker_file) as f:
        contents = f.read()

    return sha256_str(contents)


##


def read_docker_tar_image_tag(tar_file: str) -> str:
    with tarfile.open(tar_file) as tf:
        with contextlib.closing(check.not_none(tf.extractfile('manifest.json'))) as mf:
            m = mf.read()

    manifests = json.loads(m.decode('utf-8'))
    manifest = check.single(manifests)
    tag = check.non_empty_str(check.single(manifest['RepoTags']))
    return tag


def read_docker_tar_image_id(tar_file: str) -> str:
    with tarfile.open(tar_file) as tf:
        with contextlib.closing(check.not_none(tf.extractfile('index.json'))) as mf:
            i = mf.read()

    index = json.loads(i.decode('utf-8'))
    manifest = check.single(index['manifests'])
    image_id = check.non_empty_str(manifest['digest'])
    return image_id


##


def is_docker_image_present(image: str) -> bool:
    out = subprocesses.check_output(
        'docker',
        'images',
        '--format', 'json',
        image,
    )

    out_s = out.decode('utf-8').strip()
    if not out_s:
        return False

    json.loads(out_s)  # noqa
    return True


def pull_docker_image(
        image: str,
) -> None:
    subprocesses.check_call(
        'docker',
        'pull',
        image,
    )


def build_docker_image(
        docker_file: str,
        *,
        cwd: ta.Optional[str] = None,
) -> str:
    id_file = make_temp_file()
    with defer(lambda: os.unlink(id_file)):
        subprocesses.check_call(
            'docker',
            'build',
            '-f', os.path.abspath(docker_file),
            '--iidfile', id_file,
            '--squash',
            '.',
            **(dict(cwd=cwd) if cwd is not None else {}),
        )

        with open(id_file) as f:
            image_id = check.single(f.read().strip().splitlines()).strip()

    return image_id


##


def save_docker_tar_cmd(
        image: str,
        output_cmd: ShellCmd,
) -> None:
    cmd = dc.replace(output_cmd, s=f'docker save {image} | {output_cmd.s}')
    cmd.run(subprocesses.check_call)


def save_docker_tar(
        image: str,
        tar_file: str,
) -> None:
    return save_docker_tar_cmd(
        image,
        ShellCmd(f'cat {shlex.quote(tar_file)}'),
    )


#


def load_docker_tar_cmd(
        input_cmd: ShellCmd,
) -> str:
    cmd = dc.replace(input_cmd, s=f'{input_cmd.s} | docker load')

    out = cmd.run(subprocesses.check_output).decode()

    line = check.single(out.strip().splitlines())
    loaded = line.partition(':')[2].strip()
    return loaded


def load_docker_tar(
        tar_file: str,
) -> str:
    return load_docker_tar_cmd(ShellCmd(f'cat {shlex.quote(tar_file)}'))
