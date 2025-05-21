import dataclasses as dc

from ..api import append_class_metadata
from ..api import dataclass
from ..reflection import reflect


@dc.dataclass(frozen=True)
class FooMeta:
    s: str


class NewClass:
    x: int


append_class_metadata(NewClass, FooMeta('new'))
dataclass(NewClass)


class OldClass:
    x: int


append_class_metadata(OldClass, FooMeta('old'))
dc.dataclass(OldClass)


def test_old_style_classes_get_user_metadata():
    assert reflect(NewClass).spec.metadata_by_type[FooMeta] == [FooMeta('new')]
    assert reflect(OldClass).spec.metadata_by_type[FooMeta] == [FooMeta('old')]
