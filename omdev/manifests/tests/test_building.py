import os.path

import pytest

from ..building import ManifestBuilder


@pytest.mark.asyncs('asyncio')
async def test_dumping():
    mb = ManifestBuilder(
        os.path.join(os.path.dirname(__file__), 'packages'),
    )

    ms = await mb.build_package_manifests('foo')
    print(ms)
