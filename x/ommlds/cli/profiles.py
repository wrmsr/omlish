import abc
import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang
from omcore.argparse import all as ap

from .configs import EntrypointConfig


EntrypointConfigT = ta.TypeVar('EntrypointConfigT', bound=EntrypointConfig)
EntrypointConfigU = ta.TypeVar('EntrypointConfigU', bound=EntrypointConfig)


##


class Profile(lang.Abstract, ta.Generic[EntrypointConfigT]):
    @abc.abstractmethod
    def configure(self, argv: ta.Sequence[str]) -> EntrypointConfigT:
        raise NotImplementedError


##


class ProfileAspect(lang.Abstract, ta.Generic[EntrypointConfigT]):
    @property
    def name(self) -> str:
        return lang.camel_to_snake(type(self).__name__).lower()

    @property
    def default_parser_arg_group(self) -> str | None:
        return self.name

    @property
    def parser_args(self) -> ta.Sequence[ap.Arg]:
        return []

    @ta.final
    @dc.dataclass(frozen=True)
    class ConfigureContext(ta.Generic[EntrypointConfigU]):
        profile: Profile[EntrypointConfigU]
        args: ap.Namespace

    @abc.abstractmethod
    def configure(self, ctx: ConfigureContext[EntrypointConfigT], cfg: EntrypointConfigT) -> EntrypointConfigT:
        raise NotImplementedError


class AspectProfile(Profile[EntrypointConfigT], lang.Abstract):
    @abc.abstractmethod
    def _build_aspects(self) -> ta.Sequence[ProfileAspect[EntrypointConfigT]]:
        return []

    __aspects: ta.Sequence[ProfileAspect[EntrypointConfigT]]

    @ta.final
    @property
    def aspects(self) -> ta.Sequence[ProfileAspect[EntrypointConfigT]]:
        try:
            return self.__aspects
        except AttributeError:
            pass
        self.__aspects = aspects = tuple(self._build_aspects())
        return aspects

    #

    @abc.abstractmethod
    def initial_config(self) -> EntrypointConfigT:
        raise NotImplementedError

    #

    def configure(self, argv: ta.Sequence[str]) -> EntrypointConfigT:
        parser = ap.ArgumentParser()

        pa_grps: dict[str, ta.Any] = {}
        for a in self.aspects:
            for pa in a.parser_args:
                if (pa_gn := lang.opt_coalesce(pa.group, a.default_parser_arg_group)) is not None:
                    check.non_empty_str(pa_gn)
                    try:
                        pa_grp = pa_grps[pa_gn]
                    except KeyError:
                        pa_grps[pa_gn] = pa_grp = parser.add_argument_group(pa_gn)
                    pa_grp.add_argument(*pa.args, **pa.kwargs)
                else:
                    parser.add_argument(*pa.args, **pa.kwargs)

        args = parser.parse_args(argv)

        cfg_ctx = ProfileAspect.ConfigureContext(
            self,
            args,
        )
        cfg = self.initial_config()
        for a in self.aspects:
            cfg = a.configure(cfg_ctx, cfg)

        return cfg
