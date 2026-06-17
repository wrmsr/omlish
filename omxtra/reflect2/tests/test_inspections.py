# ruff: noqa: SLF001
from ..inspections import InspectionCache


def test_inspection_cache_skips_unhashable_sources() -> None:
    inspections = InspectionCache()
    source: list[int] = []
    calls = 0

    def factory() -> object:
        nonlocal calls

        calls += 1
        return object()

    left = inspections.cached_inspection('kind', source, factory)
    right = inspections.cached_inspection('kind', source, factory)

    assert left is not right
    assert calls == 2
    assert inspections._inspection_cache == {}


def test_inspection_cache_keys_include_kind_and_object() -> None:
    inspections = InspectionCache()
    source = object()
    left = object()
    right = object()

    assert inspections.cached_inspection('left', source, lambda: left) is left
    assert inspections.cached_inspection('right', source, lambda: right) is right
    assert inspections.cached_inspection('left', source, lambda: object()) is left
    assert inspections.cached_inspection('right', source, lambda: object()) is right
