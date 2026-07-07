# ruff: noqa: SLF001
from ..mirrorimpl import MirrorImpl


def test_mirrorimpl():
    mirror = MirrorImpl()
    reflector = mirror._internal

    for ty, tn in reflector._fullnames_by_type.items():
        reflector.get_type_info(ty)  # type: ignore[arg-type]
        reflector.get_type_info(tn)

    for ty in reflector._fullnames_by_type:
        reflector.reflect_type(ty)

    # placeholder for runtime inspection
    assert mirror
