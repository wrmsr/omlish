# ruff: noqa: UP006 UP007 UP045
"""
TODO:
 - some less stupid Dockerfile hash
  - doesn't change too much though
"""
import contextlib
import json
import tarfile

from omlish.lite.check import check

from ..utils import sha256_str


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
