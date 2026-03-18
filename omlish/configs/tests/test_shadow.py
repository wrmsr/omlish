import os.path
import tempfile

from ...os.shadow import ManglingShadowPaths
from ..shadow import FileShadowConfigsImpl


def test_mangled() -> None:
    tmp_dir = tempfile.mkdtemp()
    scs = FileShadowConfigsImpl(ManglingShadowPaths(tmp_dir), 'config')
    print(scs.get_shadow_config_file_path(os.path.dirname(__file__), 'barf', preferred_ext='yml'))
