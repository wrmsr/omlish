# ruff: noqa: UP006 UP007
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

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
from omlish.lite.check import check
from omlish.os.temp import temp_file_context

from .shell import ShellCmd
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


async def is_docker_image_present(image: str) -> bool:
    out = await asyncio_subprocesses.check_output(
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


async def pull_docker_image(
        image: str,
) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'pull',
        image,
    )


async def build_docker_image(
        docker_file: str,
        *,
        tag: ta.Optional[str] = None,
        cwd: ta.Optional[str] = None,
        run_options: ta.Optional[ta.Sequence[str]] = None,
) -> str:
    with temp_file_context() as id_file:
        await asyncio_subprocesses.check_call(
            'docker',
            'build',
            '-f', os.path.abspath(docker_file),
            '--iidfile', id_file,
            *(['--tag', tag] if tag is not None else []),
            *(run_options or []),
            '.',
            **(dict(cwd=cwd) if cwd is not None else {}),
        )

        with open(id_file) as f:  # noqa
            image_id = check.single(f.read().strip().splitlines()).strip()

    return image_id


async def tag_docker_image(image: str, tag: str) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'tag',
        image,
        tag,
    )


async def delete_docker_tag(tag: str) -> None:
    await asyncio_subprocesses.check_call(
        'docker',
        'rmi',
        tag,
    )


##


async def save_docker_tar_cmd(
        image: str,
        output_cmd: ShellCmd,
) -> None:
    cmd = dc.replace(output_cmd, s=f'docker save {image} | {output_cmd.s}')
    await cmd.run(asyncio_subprocesses.check_call)


async def save_docker_tar(
        image: str,
        tar_file: str,
) -> None:
    return await save_docker_tar_cmd(
        image,
        ShellCmd(f'cat > {shlex.quote(tar_file)}'),
    )


#


async def load_docker_tar_cmd(
        input_cmd: ShellCmd,
) -> str:
    cmd = dc.replace(input_cmd, s=f'{input_cmd.s} | docker load')

    out = (await cmd.run(asyncio_subprocesses.check_output)).decode()

    line = check.single(out.strip().splitlines())
    loaded = line.partition(':')[2].strip()
    return loaded


async def load_docker_tar(
        tar_file: str,
) -> str:
    return await load_docker_tar_cmd(ShellCmd(f'cat {shlex.quote(tar_file)}'))
