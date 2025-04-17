"""
TODO:
 - find_vars
"""
import abc
import dataclasses as dc
import string
import typing as ta

from .. import lang
from .minja import MinjaTemplate
from .minja import MinjaTemplateParam
from .minja import compile_minja_template


if ta.TYPE_CHECKING:
    import jinja2
else:
    jinja2 = lang.proxy_import('jinja2')


##


class Templater(lang.Abstract):
    @dc.dataclass(frozen=True)
    class Context:
        env: ta.Mapping[str, ta.Any] | None = None

    @abc.abstractmethod
    def render(self, ctx: Context) -> str:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class FormatTemplater(Templater):
    """https://docs.python.org/3/library/string.html#format-specification-mini-language"""

    fmt: str

    def render(self, ctx: Templater.Context) -> str:
        return self.fmt.format(**(ctx.env or {}))


##


@dc.dataclass(frozen=True)
class Pep292Templater(Templater):
    """https://peps.python.org/pep-0292/"""

    tmpl: string.Template

    def render(self, ctx: Templater.Context) -> str:
        return self.tmpl.substitute(ctx.env or {})

    @classmethod
    def from_string(cls, src: str) -> 'Pep292Templater':
        return cls(string.Template(src))

##


@dc.dataclass(frozen=True)
class MinjaTemplater(Templater):
    tmpl: MinjaTemplate

    ENV_IDENT: ta.ClassVar[str] = 'env'

    def render(self, ctx: Templater.Context) -> str:
        return self.tmpl(**{self.ENV_IDENT: ctx.env or {}})

    @classmethod
    def from_string(
            cls,
            src: str,
            **ns: ta.Any,
    ) -> 'MinjaTemplater':
        tmpl = compile_minja_template(
            src,
            [
                MinjaTemplateParam(cls.ENV_IDENT),
                *[
                    MinjaTemplateParam.new(k, v)
                    for k, v in ns.items()
                ],
            ],
        )

        return cls(tmpl)


##


@dc.dataclass(frozen=True)
class JinjaTemplater(Templater):
    tmpl: 'jinja2.Template'

    def render(self, ctx: Templater.Context) -> str:
        return self.tmpl.render(**(ctx.env or {}))

    @classmethod
    def from_string(
            cls,
            src: str,
            *,
            env: ta.Optional['jinja2.Environment'] = None,
            **kwargs: ta.Any,
    ) -> 'JinjaTemplater':
        if env is None:
            env = jinja2.Environment()
        tmpl = env.from_string(src)
        return cls(
            tmpl,
            **kwargs,
        )
