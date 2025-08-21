import sys

from .resolving import resolve_import_name


##


# dict[str, None] to preserve insertion order - we don't have OrderedSet here
_REGISTERED_CONDITIONAL_IMPORTS: dict[str, dict[str, None] | None] = {}


def register_conditional_import(when: str, then: str, package: str | None = None) -> None:
    wn = resolve_import_name(when, package)
    tn = resolve_import_name(then, package)
    if tn in sys.modules:
        return
    if wn in sys.modules:
        __import__(tn)
    else:
        tns = _REGISTERED_CONDITIONAL_IMPORTS.setdefault(wn, {})
        if tns is None:
            raise Exception(f'Conditional import trigger already cleared: {wn=} {tn=}')
        tns[tn] = None


def trigger_conditional_imports(package: str) -> None:
    tns = _REGISTERED_CONDITIONAL_IMPORTS.get(package, {})
    if tns is None:
        raise Exception(f'Conditional import trigger already cleared: {package=}')
    _REGISTERED_CONDITIONAL_IMPORTS[package] = None
    for tn in tns:
        __import__(tn)
