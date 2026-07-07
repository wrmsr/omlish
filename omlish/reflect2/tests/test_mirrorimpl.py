# ruff: noqa: SLF001
from ..mirrorimpl import MirrorImpl


def test_mirrorimpl():
    mirror = MirrorImpl()

    universe = mirror._universe
    for ty, tn in universe.fullnames_by_type.items():
        universe.get_type_info(ty)  # type: ignore[arg-type]
        universe.get_type_info(tn)

    reflector = mirror._reflector
    for ty in universe.fullnames_by_type:
        reflector.reflect_type(ty)

    # placeholder for runtime inspection
    assert mirror
