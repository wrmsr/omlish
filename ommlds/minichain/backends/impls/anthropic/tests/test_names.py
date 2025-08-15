from omlish.manifests.globals import GlobalManifestLoader


def test_names():
    manifests = GlobalManifestLoader.load(__package__.partition('.')[0])
    print(manifests)
