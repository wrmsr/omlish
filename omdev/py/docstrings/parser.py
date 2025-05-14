"""The main parsing routine."""
import inspect
import typing as ta

from . import epydoc
from . import google
from . import numpydoc
from . import rest
from .attrdoc import add_attribute_docstrings
from .common import Docstring
from .common import DocstringStyle
from .common import ParseError


##


_STYLE_MAP = {
    DocstringStyle.REST: rest,
    DocstringStyle.GOOGLE: google,
    DocstringStyle.NUMPYDOC: numpydoc,
    DocstringStyle.EPYDOC: epydoc,
}


def parse(
        text: str,
        style: DocstringStyle = DocstringStyle.AUTO,
) -> Docstring:
    """
    Parse the docstring into its components.

    :param text: docstring text to parse
    :param style: docstring style
    :returns: parsed docstring representation
    """

    if style != DocstringStyle.AUTO:
        return _STYLE_MAP[style].parse(text)

    exc: Exception | type[Exception] = ParseError
    rets = []
    for module in _STYLE_MAP.values():
        try:
            ret = module.parse(text)
        except ParseError as ex:
            exc = ex
        else:
            rets.append(ret)

    if not rets:
        raise exc

    return sorted(rets, key=lambda d: len(d.meta), reverse=True)[0]


def parse_from_object(
        obj: ta.Any,
        style: DocstringStyle = DocstringStyle.AUTO,
) -> Docstring:
    """
    Parse the object's docstring(s) into its components.

    The object can be anything that has a ``__doc__`` attribute. In contrast to the ``parse`` function,
    ``parse_from_object`` is able to parse attribute docstrings which are defined in the source code instead of
    ``__doc__``.

    Currently only attribute docstrings defined at class and module levels are supported. Attribute docstrings defined
    in ``__init__`` methods are not supported.

    When given a class, only the attribute docstrings of that class are parsed, not its inherited classes. This is a
    design decision. Separate calls to this function should be performed to get attribute docstrings of parent classes.

    :param obj: object from which to parse the docstring(s)
    :param style: docstring style
    :returns: parsed docstring representation
    """

    docstring = parse(obj.__doc__, style=style)

    if inspect.isclass(obj) or inspect.ismodule(obj):
        add_attribute_docstrings(obj, docstring)

    return docstring
