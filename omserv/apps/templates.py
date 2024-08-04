import dataclasses as dc
import importlib.resources
import logging
import typing as ta

import jinja2

from .base import url_for


log = logging.getLogger(__name__)


##


J2_DEFAULT_NAMESPACE = {}


def j2_helper(fn):
    J2_DEFAULT_NAMESPACE[fn.__name__] = fn
    return fn


j2_helper(url_for)


##


J2Namespace = ta.NewType('J2Namespace', ta.Mapping[str, ta.Any])


class J2Templates:
    @dc.dataclass(frozen=True)
    class Config:
        resource_root: str
        reload: bool = False

    def __init__(self, config: Config, ns: J2Namespace) -> None:
        super().__init__()

        self._config = config
        self._ns = ns

        self._env = jinja2.Environment(
            loader=self._Loader(self),
            autoescape=True,
        )

        self._all: ta.Mapping[str, jinja2.Template] | None = None

    class _Loader(jinja2.BaseLoader):
        def __init__(self, owner: 'J2Templates') -> None:
            super().__init__()
            self._owner = owner

        def get_source(self, environment, template):
            raise TypeError

        def list_templates(self):
            raise TypeError

        def load(self, environment, name, globals=None):  # noqa
            return self._owner.load(name)

    def _load_all(self) -> ta.Mapping[str, jinja2.Template]:
        ret: dict[str, jinja2.Template] = {}
        for fn in importlib.resources.files(self._config.resource_root).iterdir():
            if fn.name.endswith('.j2'):
                ret[fn.name] = self._env.from_string(fn.read_text())
        return ret

    def load_all(self) -> ta.Mapping[str, jinja2.Template]:
        if self._config.reload:
            return self._load_all()

        if self._all is None:
            self._all = self._load_all()
        return self._all

    def load(self, name: str) -> jinja2.Template:
        return self.load_all()[name]

    def render(self, template_name: str, **kwargs: ta.Any) -> bytes:
        return self.load(template_name).render(**{
            **J2_DEFAULT_NAMESPACE,
            **self._ns,
            **kwargs,
        }).encode()
