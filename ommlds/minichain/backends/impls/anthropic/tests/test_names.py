from omlish.manifests.globals import MANIFEST_LOADER


def test_names():
    manifests = MANIFEST_LOADER.load(__package__.partition('.')[0])
    print(manifests)
