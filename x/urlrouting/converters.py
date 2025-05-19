import re
import typing as ta
import urllib.parse
import uuid


if ta.TYPE_CHECKING:
    from .map import Map


##


class ValidationError(ValueError):
    """
    Validation error.  If a rule converter raises this exception the rule does not match the current URL and the next
    URL is tried.
    """


class BaseConverter:
    """Base class for all converters."""

    regex = '[^/]+'
    weight = 100
    part_isolating = True

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        # If the converter isn't inheriting its regex, disable part_isolating by default if the regex contains a /
        # character.
        if 'regex' in cls.__dict__ and 'part_isolating' not in cls.__dict__:
            cls.part_isolating = '/' not in cls.regex

    def __init__(self, map: 'Map', *args: ta.Any, **kwargs: ta.Any) -> None:  # noqa
        super().__init__()

        self.map = map

    def to_python(self, value: str) -> ta.Any:
        return value

    def to_url(self, value: ta.Any) -> str:
        # safe = https://url.spec.whatwg.org/#url-path-segment-string
        return urllib.parse.quote(str(value), safe="!$&'()*+,/:;=@")


class UnicodeConverter(BaseConverter):
    """
    This converter is the default converter and accepts any string but only one path segment.  Thus the string can not
    include a slash.

    This is the default validator.

    Example::

        Rule('/pages/<page>'),
        Rule('/<string(length=2):lang_code>')

    :param map: the :class:`Map`.
    :param minlength: the minimum length of the string.  Must be greater or equal 1.
    :param maxlength: the maximum length of the string.
    :param length: the exact length of the string.
    """

    def __init__(
            self,
            map: 'Map',  # noqa
            minlength: int = 1,
            maxlength: int | None = None,
            length: int | None = None,
    ) -> None:
        super().__init__(map)

        if length is not None:
            length_regex = f'{{{int(length)}}}'
        else:
            if maxlength is None:
                maxlength_value = ''
            else:
                maxlength_value = str(int(maxlength))
            length_regex = f'{{{int(minlength)},{maxlength_value}}}'
        self.regex = f'[^/]{length_regex}'


class AnyConverter(BaseConverter):
    """
    Matches one of the items provided.  Items can either be Python identifiers or strings::

        Rule('/<any(about, help, imprint, class, "foo,bar"):page_name>')

    :param map: the :class:`Map`.
    :param items: this function accepts the possible items as positional arguments.
    """

    def __init__(self, map: 'Map', *items: str) -> None:  # noqa
        super().__init__(map)

        self.items = set(items)
        self.regex = f"(?:{'|'.join([re.escape(x) for x in items])})"

    def to_url(self, value: ta.Any) -> str:
        if value in self.items:
            return str(value)

        valid_values = ', '.join(f"'{item}'" for item in sorted(self.items))
        raise ValueError(f"'{value}' is not one of {valid_values}")


class PathConverter(BaseConverter):
    """
    Like the default :class:`UnicodeConverter`, but it also matches slashes.  This is useful for wikis and similar
    applications::

        Rule('/<path:wikipage>')
        Rule('/<path:wikipage>/edit')

    :param map: the :class:`Map`.
    """

    part_isolating = False
    regex = '[^/].*?'
    weight = 200


class _NumberConverter(BaseConverter):
    """Baseclass for `IntegerConverter` and `FloatConverter`."""

    weight = 50
    num_convert: ta.Callable[[ta.Any], ta.Any] = int

    def __init__(
            self,
            map: 'Map',  # noqa
            fixed_digits: int = 0,
            min: float | None = None,  # noqa
            max: float | None = None,  # noqa
            signed: bool = False,
    ) -> None:
        if signed:
            self.regex = self.signed_regex

        super().__init__(map)

        self.fixed_digits = fixed_digits
        self.min = min
        self.max = max
        self.signed = signed

    def to_python(self, value: str) -> ta.Any:
        if self.fixed_digits and len(value) != self.fixed_digits:
            raise ValidationError

        value_num = self.num_convert(value)
        if (
                (self.min is not None and value_num < self.min) or
                (self.max is not None and value_num > self.max)
        ):
            raise ValidationError

        return value_num

    def to_url(self, value: ta.Any) -> str:
        value_str = str(self.num_convert(value))
        if self.fixed_digits:
            value_str = value_str.zfill(self.fixed_digits)
        return value_str

    @property
    def signed_regex(self) -> str:
        return f'-?{self.regex}'


class IntegerConverter(_NumberConverter):
    """
    This converter only accepts integer values::

        Rule("/page/<int:page>")

    By default it only accepts unsigned, positive values. The ``signed`` parameter will enable signed, negative values.
    ::

        Rule("/page/<int(signed=True):page>")

    :param map: The :class:`Map`.
    :param fixed_digits: The number of fixed digits in the URL. If you set this to ``4`` for example, the rule will only
        match if the URL looks like ``/0001/``. The default is variable length.
    :param min: The minimal value.
    :param max: The maximal value.
    :param signed: Allow signed (negative) values.
    """

    regex = r'\d+'


class FloatConverter(_NumberConverter):
    """
    This converter only accepts floating point values::

        Rule("/probability/<float:probability>")

    By default it only accepts unsigned, positive values. The ``signed`` parameter will enable signed, negative values.
    ::

        Rule("/offset/<float(signed=True):offset>")

    :param map: The :class:`Map`.
    :param min: The minimal value.
    :param max: The maximal value.
    :param signed: Allow signed (negative) values.
    """

    regex = r'\d+\.\d+'
    num_convert = float

    def __init__(
            self,
            map: 'Map',  # noqa
            min: float | None = None,  # noqa
            max: float | None = None,  # noqa
            signed: bool = False,
    ) -> None:
        super().__init__(
            map,
            min=min,
            max=max,
            signed=signed,
        )


class UuidConverter(BaseConverter):
    """
    This converter only accepts UUID strings::

        Rule('/object/<uuid:identifier>')

    :param map: the :class:`Map`.
    """

    regex = (
        r'[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-'
        r'[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}'
    )

    def to_python(self, value: str) -> uuid.UUID:
        return uuid.UUID(value)

    def to_url(self, value: uuid.UUID) -> str:
        return str(value)


# the default converter mapping for the map.
DEFAULT_CONVERTERS: ta.Mapping[str, type[BaseConverter]] = {
    'default': UnicodeConverter,
    'string': UnicodeConverter,
    'any': AnyConverter,
    'path': PathConverter,
    'int': IntegerConverter,
    'float': FloatConverter,
    'uuid': UuidConverter,
}
