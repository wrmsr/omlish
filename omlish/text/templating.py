"""
TODO:
 - find_vars
 - some kind of EnvKey / EnvMarker(lang.Marker), namespace-able env keys - but how to weave these into tmpl srcs?
"""
import abc
import dataclasses as dc
import string
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import jinja2

    from . import minja

else:
    jinja2 = lang.proxy_import('jinja2')

    minja = lang.proxy_import('.minja', __package__)


##


class Templater(lang.Abstract):
    """
    This is named a 'templatER', not 'template', because it probably refers to a bigger thing itself called a
    'template' (like a `jinja2.Template`).
    """

    @dc.dataclass(frozen=True)
    class Context:
        env: ta.Mapping[str, ta.Any] | None = None

    @abc.abstractmethod
    def render(self, ctx: Context) -> str:
        raise NotImplementedError


def templater_context(
        *envs: ta.Mapping[str, ta.Any] | None,
        strict: bool = False,
) -> Templater.Context:
    env: dict[str, ta.Any] = {}
    for e in envs:
        if e is None:
            continue
        for k, v in e.items():
            if strict and k in env:
                raise KeyError(k)
            env[k] = v

    return Templater.Context(
        env=env or None,
    )


##


@dc.dataclass(frozen=True)
class FormatTemplater(Templater):
    """https://docs.python.org/3/library/string.html#format-specification-mini-language"""

    fmt: str

    def render(self, ctx: Templater.Context) -> str:
        return self.fmt.format(**(ctx.env or {}))


format_templater = FormatTemplater


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


pep292_templater = Pep292Templater.from_string


##


@dc.dataclass(frozen=True)
class MinjaTemplater(Templater):
    tmpl: 'minja.MinjaTemplate'

    ENV_IDENT: ta.ClassVar[str] = 'env'

    def render(self, ctx: Templater.Context) -> str:
        return self.tmpl(**{self.ENV_IDENT: ctx.env or {}})

    @classmethod
    def from_string(
            cls,
            src: str,
            **ns: ta.Any,
    ) -> 'MinjaTemplater':
        tmpl = minja.compile_minja_template(
            src,
            [
                minja.MinjaTemplateParam(cls.ENV_IDENT),
                *[
                    minja.MinjaTemplateParam.new(k, v)
                    for k, v in ns.items()
                ],
            ],
        )

        return cls(tmpl)


minja_templater = MinjaTemplater.from_string


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


jinja_templater = JinjaTemplater.from_string
