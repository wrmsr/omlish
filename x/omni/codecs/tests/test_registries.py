from .. import registries as registries_
from .. import types as types_


def test_registries():
    assert issubclass(registries_.EXTENSION_REGISTRY['gz'], types_.Codec)

    gz_lines_codec = registries_.for_extension('lines.gz')
    assert isinstance(gz_lines_codec, types_.Codec)
