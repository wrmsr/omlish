import tempfile

from ..shadow import MangledFilesShadowConfigs


def test_mangled() -> None:
    tmp_dir = tempfile.mkdtemp()
    scs = MangledFilesShadowConfigs(tmp_dir)
    print(scs.get_shadow_config_file_path(__file__))
