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
