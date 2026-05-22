from .functions import Functions
from .runtime import Runtime


##


class Options:
    """Options to control how a Jmespath function is evaluated."""

    def __init__(
            self,
            dict_cls: type | None = None,
            custom_functions: Functions | None = None,
            enable_legacy_literals: bool = False,
            runtime: Runtime | None = None,
    ) -> None:
        super().__init__()

        # The class to use when creating a dict.  The interpreter may create dictionaries during the evaluation of a
        # Jmespath expression.  For example, a multi-select hash will create a dictionary.  By default we use a dict()
        # type. You can set this value to change what dict type is used. The most common reason you would change this is
        # if you want to set a collections.OrderedDict so that you can have predictable key ordering.
        self.dict_cls = dict_cls
        self.custom_functions = custom_functions
        self.runtime = runtime

        # The flag to enable pre-JEP-12 literal compatibility.
        # JEP-12 deprecates `foo` -> "foo" syntax.
        # Valid expressions MUST use: `"foo"` -> "foo"
        # Setting this flag to `True` enables support for legacy syntax.
        self.enable_legacy_literals = enable_legacy_literals
