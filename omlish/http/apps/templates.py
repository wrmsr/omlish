import abc
import dataclasses as dc
import importlib.resources
import typing as ta

from ... import check
from ... import lang
from ...logs import all as logs
from ...text import templating as tpl
from .base import url_for


with lang.auto_proxy_import(globals()):
    import jinja2


log = logs.get_module_logger(globals())


##


TEMPLATE_DEFAULT_NAMESPACE: ta.Mapping[str, ta.Callable] = {}


def default_template_helper(fn):
    check.not_in(n := fn.__name__, TEMPLATE_DEFAULT_NAMESPACE)
    ta.cast(ta.Any, TEMPLATE_DEFAULT_NAMESPACE)[n] = fn
    return fn


default_template_helper(url_for)


##


TemplateNamespace = ta.NewType('TemplateNamespace', ta.Mapping[str, ta.Any])


class Templates:
    @dc.dataclass(frozen=True)
    class Config:
        resource_root: str
        reload: bool = False

    def __init__(
            self,
            config: Config,
            ns: TemplateNamespace,
    ) -> None:
        super().__init__()

        self._config = config
        self._ns = ns

        self._all: ta.Mapping[str, tpl.Templater] | None = None

    @property
    @abc.abstractmethod
    def _file_extensions(self) -> ta.AbstractSet[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def _build_one(self, s: str) -> tpl.Templater:
        raise NotImplementedError

    def _load_all(self) -> ta.Mapping[str, tpl.Templater]:
        exts = self._file_extensions
        ret: dict[str, tpl.Templater] = {}

        for fn in importlib.resources.files(self._config.resource_root).iterdir():  # noqa
            if any(fn.name.endswith(ext) for ext in exts):
                ret[fn.name] = self._build_one(fn.read_text())

        return ret

    def load_all(self) -> ta.Mapping[str, tpl.Templater]:
        if self._config.reload:
            return self._load_all()

        if self._all is None:
            self._all = self._load_all()
        return self._all

    def load(self, name: str) -> tpl.Templater:
        return self.load_all()[name]

    def render(self, template_name: str, **kwargs: ta.Any) -> bytes:
        return self.load(template_name).render(tpl.Templater.Context(env={
            **TEMPLATE_DEFAULT_NAMESPACE,
            **self._ns,
            **kwargs,
        })).encode()


class JinjaTemplates(Templates):
    def __init__(
            self,
            config: Templates.Config,
            ns: TemplateNamespace,
    ) -> None:
        super().__init__(
            config,
            ns,
        )

        self._env = jinja2.Environment(
            loader=self._loader_cls()(self),
            autoescape=True,
        )

    _loader_cls_: ta.Any

    @classmethod
    def _loader_cls(cls) -> type:
        try:
            return cls._loader_cls_
        except AttributeError:
            pass

        class _Loader(jinja2.BaseLoader):  # noqa
            def __init__(self, owner: 'JinjaTemplates') -> None:
                super().__init__()

                self._owner = owner

            def get_source(self, environment, template):
                raise TypeError

            def list_templates(self):
                raise TypeError

            def load(self, environment, name, globals=None):  # noqa
                return check.isinstance(self._owner.load(name), tpl.JinjaTemplater).tmpl

        return _Loader

    @property
    def _file_extensions(self) -> ta.AbstractSet[str]:
        return {'.j2'}

    def _build_one(self, s: str) -> tpl.Templater:
        return tpl.JinjaTemplater.from_string(
            s,
            env=self._env,
        )
