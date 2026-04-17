from omlish.manifests.globals import GlobalManifestLoader

from ....registries.globals import get_global_registry
from ...strings.manifests import BackendStringsManifest


def test_strings():
    bsms = GlobalManifestLoader.load_values_of(BackendStringsManifest)

    for bsm in bsms:
        print(bsm)
        for scn in bsm.service_cls_names:
            print(get_global_registry().get_registry_type_cls(scn))
        print()
