"""
TODO:
 - vs ta.get_type_hints?
"""
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import inspect
else:
    inspect = lang.proxy_import('inspect')


annotationlib = lang.lazy_import('annotationlib', optional=True, cache_failure=True)


def get_annotations(obj: ta.Any) -> ta.Mapping[str, ta.Any]:
    if (al := annotationlib()) is not None:
        return al.get_annotations(obj, format=al.Format.FORWARDREF)  # noqa
    else:
        return inspect.get_annotations(obj)
