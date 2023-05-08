from .. import argspecs as as_
from .. import names as names_


def test_argspecs():
    assert as_.render_arg_spec_def(as_.ArgSpec(['a']), names_.NamespaceBuilder()) == '(a)'
    assert as_.render_arg_spec_def(as_.ArgSpec(['a'], kwonlyargs=['b']), names_.NamespaceBuilder()) == '(a, *, b)'
    assert as_.render_arg_spec_def(as_.ArgSpec(['a'], kwonlyargs=['b', 'c'], kwonlydefaults={'c': 0}), names_.NamespaceBuilder()) == '(a, *, b, c=_c_default)'  # noqa
