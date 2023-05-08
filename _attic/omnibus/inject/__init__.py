"""
A dependency injection system heavily inspired by Guice (specifically MiniGuice). Supports annotation powered
introspection, private modules, set and dict binders, and Guice-style scopes and child injectors, with intended support
for proxies / circular injection, type converters, and overriding modules as needed. Being aware of the two-dozen odd
other python DI systems I'm still happiest with mine, basically 'doing what Guice does' (impl-wise, not just skin deep)
but with a tenth the complexity (python kwargs over builders, little regard for its error messages as its graphs tend to
be smaller, etc).
"""
from .bind import annotate  # noqa
from .bind import create_binder  # noqa
from .bind import create_private_binder  # noqa
from .inject import create_injector  # noqa
from .types import Binder  # noqa
from .types import Binding  # noqa
from .types import InjectionError  # noqa
from .types import Injector  # noqa
from .types import InjectorConfig  # noqa
from .types import Key  # noqa
from .types import PrivateBinder  # noqa
from .types import Scope  # noqa
