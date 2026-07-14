# import pytest
#
# from ..loading import ManifestLoader
#
#
# def test_fix_class_key():
#     assert ManifestLoader._fix_class_key(
#         '$.abc.de.gh',
#         'barf.foo.bar.baz',
#     ) == '$barf.foo.bar.abc.de.gh'
#     assert ManifestLoader._fix_class_key(
#         '$..abc.de.gh',
#         'barf.foo.bar.baz',
#     ) == '$barf.foo.abc.de.gh'
#     assert ManifestLoader._fix_class_key(
#         '$...abc.de.gh',
#         'barf.foo.bar.baz',
#     ) == '$barf.abc.de.gh'
#     with pytest.raises(ManifestLoader.ClassKeyError):
#         assert ManifestLoader._fix_class_key(
#             '$....abc.de.gh',
#             'barf.foo.bar.baz',
#         ) == '$abc.de.gh'
