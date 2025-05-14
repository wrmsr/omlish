"""Common methods for parsing."""
import enum


##


PARAM_KEYWORDS = {
    'arg',
    'argument',
    'attribute',
    'key',
    'keyword',
    'param',
    'parameter',
}

RAISES_KEYWORDS = {
    'except',
    'exception',
    'raise',
    'raises',
}

DEPRECATION_KEYWORDS = {
    'deprecated',
    'deprecation',
}

RETURNS_KEYWORDS = {
    'return',
    'returns',
}

YIELDS_KEYWORDS = {
    'yield',
    'yields',
}

EXAMPLES_KEYWORDS = {
    'example',
    'examples',
}


##


class ParseError(RuntimeError):
    """Base class for all parsing related errors."""


##


class DocstringStyle(enum.Enum):
    """Docstring style."""

    REST = 1
    GOOGLE = 2
    NUMPYDOC = 3
    EPYDOC = 4
    AUTO = 255


class RenderingStyle(enum.Enum):
    """Rendering style when unparsing parsed docstrings."""

    COMPACT = 1
    CLEAN = 2
    EXPANDED = 3


##


class DocstringMeta:
    """
    Docstring meta information.

    Symbolizes lines in form of

        :param arg: description
        :raises ValueError: if something happens
    """

    def __init__(
            self,
            args: list[str],
            description: str | None,
    ) -> None:
        """
        Initialize self.

        :param args: list of arguments. The exact content of this variable is dependent on the kind of docstring; it's
            used to distinguish between custom docstring meta information items.
        :param description: associated docstring description.
        """

        super().__init__()

        self.args = args
        self.description = description


class DocstringParam(DocstringMeta):
    """DocstringMeta symbolizing :param metadata."""

    def __init__(
            self,
            args: list[str],
            description: str | None,
            arg_name: str,
            type_name: str | None,
            is_optional: bool | None,
            default: str | None,
    ) -> None:
        """Initialize self."""

        super().__init__(args, description)

        self.arg_name = arg_name
        self.type_name = type_name
        self.is_optional = is_optional
        self.default = default


class DocstringReturns(DocstringMeta):
    """DocstringMeta symbolizing :returns or :yields metadata."""

    def __init__(
            self,
            args: list[str],
            description: str | None,
            type_name: str | None,
            is_generator: bool,
            return_name: str | None = None,
    ) -> None:
        """Initialize self."""

        super().__init__(args, description)

        self.type_name = type_name
        self.is_generator = is_generator
        self.return_name = return_name


class DocstringRaises(DocstringMeta):
    """DocstringMeta symbolizing :raises metadata."""

    def __init__(
            self,
            args: list[str],
            description: str | None,
            type_name: str | None,
    ) -> None:
        """Initialize self."""

        super().__init__(args, description)

        self.type_name = type_name
        self.description = description


class DocstringDeprecated(DocstringMeta):
    """DocstringMeta symbolizing deprecation metadata."""

    def __init__(
            self,
            args: list[str],
            description: str | None,
            version: str | None,
    ) -> None:
        """Initialize self."""

        super().__init__(args, description)

        self.version = version
        self.description = description


class DocstringExample(DocstringMeta):
    """DocstringMeta symbolizing example metadata."""

    def __init__(
            self,
            args: list[str],
            snippet: str | None,
            description: str | None,
    ) -> None:
        """Initialize self."""

        super().__init__(args, description)

        self.snippet = snippet
        self.description = description


##


class Docstring:
    """Docstring object representation."""

    def __init__(
            self,
            style: DocstringStyle | None = None,
    ) -> None:
        """Initialize self."""

        super().__init__()

        self.short_description: str | None = None
        self.long_description: str | None = None
        self.blank_after_short_description = False
        self.blank_after_long_description = False
        self.meta: list[DocstringMeta] = []
        self.style: DocstringStyle | None = style

    @property
    def description(self) -> str | None:
        """
        Return the full description of the function

        Returns None if the docstring did not include any description
        """

        ret = []
        if self.short_description:
            ret.append(self.short_description)
            if self.blank_after_short_description:
                ret.append('')
        if self.long_description:
            ret.append(self.long_description)

        if not ret:
            return None

        return '\n'.join(ret)

    @property
    def params(self) -> list[DocstringParam]:
        """Return a list of information on function params."""

        return [item for item in self.meta if isinstance(item, DocstringParam)]

    @property
    def raises(self) -> list[DocstringRaises]:
        """Return a list of information on the exceptions that the function may raise."""

        return [item for item in self.meta if isinstance(item, DocstringRaises)]

    @property
    def returns(self) -> DocstringReturns | None:
        """
        Return a single information on function return.

        Takes the first return information.
        """

        for item in self.meta:
            if isinstance(item, DocstringReturns):
                return item
        return None

    @property
    def many_returns(self) -> list[DocstringReturns]:
        """Return a list of information on function return."""

        return [item for item in self.meta if isinstance(item, DocstringReturns)]

    @property
    def deprecation(self) -> DocstringDeprecated | None:
        """Return a single information on function deprecation notes."""

        for item in self.meta:
            if isinstance(item, DocstringDeprecated):
                return item
        return None

    @property
    def examples(self) -> list[DocstringExample]:
        """Return a list of information on function examples."""

        return [item for item in self.meta if isinstance(item, DocstringExample)]
