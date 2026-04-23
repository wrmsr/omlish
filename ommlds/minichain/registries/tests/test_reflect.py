import typing as ta

import pytest

from omlish import reflect as rfl

from ..reflect import RegistryTypeName
from ..reflect import get_annotated_registry_type_name
from ..reflect import strip_registry_annotations


def test_get_name():
    assert get_annotated_registry_type_name(int) is None
    assert get_annotated_registry_type_name(ta.Annotated[int, 420]) is None
    assert get_annotated_registry_type_name(ta.Annotated[int, RegistryTypeName('foo')]) == 'foo'
    assert get_annotated_registry_type_name(ta.Annotated[int, 420, RegistryTypeName('foo'), 421]) == 'foo'
    with pytest.raises(ValueError):  # noqa
        get_annotated_registry_type_name(ta.Annotated[int, RegistryTypeName('foo'), RegistryTypeName('bar')])

    assert get_annotated_registry_type_name(rfl.type_(int)) is None
    assert get_annotated_registry_type_name(rfl.type_(ta.Annotated[int, 420])) is None
    assert get_annotated_registry_type_name(rfl.type_(ta.Annotated[int, RegistryTypeName('foo')])) == 'foo'
    assert get_annotated_registry_type_name(rfl.type_(ta.Annotated[int, 420, RegistryTypeName('foo'), 420])) == 'foo'
    with pytest.raises(ValueError):  # noqa
        get_annotated_registry_type_name(rfl.type_(ta.Annotated[int, RegistryTypeName('foo'), RegistryTypeName('bar')]))


def test_strip_name():
    assert strip_registry_annotations(int) is int
    assert strip_registry_annotations(ta.Annotated[int, 420]) == ta.Annotated[int, 420]
    assert strip_registry_annotations(ta.Annotated[int, RegistryTypeName('foo')]) is int
    assert strip_registry_annotations(ta.Annotated[int, 420, RegistryTypeName('foo'), 421]) == ta.Annotated[int, 420, 421]  # noqa

    assert strip_registry_annotations(rfl.type_(int)) == rfl.type_(int)
    assert strip_registry_annotations(rfl.type_(ta.Annotated[int, 420])) == rfl.type_(ta.Annotated[int, 420])
    assert strip_registry_annotations(rfl.type_(ta.Annotated[int, RegistryTypeName('foo')])) == rfl.type_(int)
    assert strip_registry_annotations(rfl.type_(ta.Annotated[int, 420, RegistryTypeName('foo'), 421])) == rfl.type_(ta.Annotated[int, 420, 421])  # noqa
