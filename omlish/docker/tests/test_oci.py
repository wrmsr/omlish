# ruff: noqa: UP006 UP007
# @omlish-lite
import unittest

from omlish.lite import marshal as msh

from ..oci import OciMediaImageIndex
from ..oci import OciMediaImageManifest


INDEX = {
    'schemaVersion': 2,
    'mediaType': 'application/vnd.oci.image.index.v1+json',
    'manifests': [
        {
            'mediaType': 'application/vnd.oci.image.manifest.v1+json',
            'digest': 'sha256:44101452bc1de6c4f788a17d1f9ffce2e72a494aabe4dada0b4e615b217cf2db',
            'size': 675,
            'platform': {
                'architecture': 'amd64',
                'os': 'linux',
            },
        },
        {
            'mediaType': 'application/vnd.oci.image.manifest.v1+json',
            'digest': 'sha256:5fed47fbacae6e46603f496390be0d2ced76ce8d7841136eda69ba6764ce2730',
            'size': 675,
            'platform': {
                'architecture': 'arm64',
                'os': 'linux',
            },
        },
        {
            'mediaType': 'application/vnd.oci.image.manifest.v1+json',
            'digest': 'sha256:ec6d04ea2896ad8b8138f588c773707c6b04e0a9a5c6bd340c1214d52b64ad12',
            'size': 566,
            'annotations': {
                'vnd.docker.reference.digest': 'sha256:44101452bc1de6c4f788a17d1f9ffce2e72a494aabe4dada0b4e615b217cf2db',  # noqa
                'vnd.docker.reference.type': 'attestation-manifest',
            },
            'platform': {
                'architecture': 'unknown',
                'os': 'unknown',
            },
        },
        {
            'mediaType': 'application/vnd.oci.image.manifest.v1+json',
            'digest': 'sha256:706c341fbec14c724aac280d8b356ff4c8932cfbe570944d63d7925258941f9e',
            'size': 566,
            'annotations': {
                'vnd.docker.reference.digest': 'sha256:5fed47fbacae6e46603f496390be0d2ced76ce8d7841136eda69ba6764ce2730',  # noqa
                'vnd.docker.reference.type': 'attestation-manifest',
            },
            'platform': {
                'architecture': 'unknown',
                'os': 'unknown',
            },
        },
    ],
    'annotations': {
        'com.wrmsr.barf': 'a',
    },
}


MANIFEST = {
    'schemaVersion': 2,
    'mediaType': 'application/vnd.oci.image.manifest.v1+json',
    'config': {
        'mediaType': 'application/vnd.oci.image.config.v1+json',
        'digest': 'sha256:7f3f8bda94563c7f83251e018d16974dd8bec283b17e85adeeb88f139a0e5a15',
        'size': 1121,
    },
    'layers': [
        {
            'mediaType': 'application/vnd.oci.image.layer.v1.tar+gzip',
            'digest': 'sha256:2cc3ae149d28a36d28d4eefbae70aaa14a0c9eab588c3790f7979f310b893c44',
            'size': 29150430,
        },
        {
            'mediaType': 'application/vnd.oci.image.layer.v1.tar+gzip',
            'digest': 'sha256:b81e0fcdc2c41cef54e3f819822c9ac15da4784f6c2e689ef901ba7d25157877',
            'size': 11568162,
        },
    ],
}


class TestOci(unittest.TestCase):
    def test_marshal(self):
        index: OciMediaImageIndex = msh.unmarshal_obj(INDEX, OciMediaImageIndex)
        print(index)

        manifest: OciMediaImageManifest = msh.unmarshal_obj(MANIFEST, OciMediaImageManifest)
        print(manifest)
