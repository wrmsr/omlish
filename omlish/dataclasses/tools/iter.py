import dataclasses as dc
import typing as ta


##


def fields_dict(cls_or_instance: ta.Any) -> dict[str, dc.Field]:
    return {f.name: f for f in dc.fields(cls_or_instance)}


##


def iter_items(obj: ta.Any) -> ta.Iterator[tuple[str, ta.Any]]:
    for f in dc.fields(obj):
        yield (f.name, getattr(obj, f.name))


def iter_keys(obj: ta.Any) -> ta.Iterator[str]:
    for f in dc.fields(obj):
        yield f.name


def iter_values(obj: ta.Any) -> ta.Iterator[ta.Any]:
    for f in dc.fields(obj):
        yield getattr(obj, f.name)


##


class FieldIterable:
    def __iter__(self) -> ta.Iterator[dc.Field]:
        return iter(dc.fields(self))  # type: ignore[arg-type]  # noqa


class FieldNameIterable:
    def __iter__(self) -> ta.Iterator[str]:
        return (f.name for f in dc.fields(self))  # type: ignore[arg-type]  # noqa


class FieldValueIterable:
    def __iter__(self) -> ta.Iterator[tuple[dc.Field, ta.Any]]:
        return ((f, getattr(self, f.name)) for f in dc.fields(self))  # type: ignore[arg-type]  # noqa


class FieldNameValueIterable:
    def __iter__(self) -> ta.Iterator[tuple[str, ta.Any]]:
        return ((f.name, getattr(self, f.name)) for f in dc.fields(self))  # type: ignore[arg-type]  # noqa
