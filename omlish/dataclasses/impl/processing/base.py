"""
TODO:
 - Configurable? class Config crtp?
  - all config on specs? prob not desirable purity, prob want ~some~ global config if only defaults
   - ProcessorConfigSpecProviderFactoryThingy?
  - FIXME: for now these are processor ctor kwargs that are never overridden
"""
import typing as ta

from .... import check
from .... import lang
from ...specs import ClassSpec


T = ta.TypeVar('T')
ProcessingOptionT = ta.TypeVar('ProcessingOptionT', bound='ProcessingOption')


##


ProcessingContextItemFactory: ta.TypeAlias = ta.Callable[['ProcessingContext'], ta.Any]


class ProcessingOption(lang.Abstract):
    pass


class ProcessingContext:
    def __init__(
            self,
            cls: type,
            cs: ClassSpec,
            item_factories: ta.Mapping[type, ProcessingContextItemFactory],
            *,
            options: ta.Sequence[ProcessingOption] | None = None,
    ) -> None:
        super().__init__()

        self._cls = cls
        self._cs = cs
        self._item_factories = item_factories

        options_dct: dict = {}
        for o in options or ():
            check.not_in(type(o), options_dct)
            options_dct[type(o)] = o
        self._options_dct = options_dct

        self._items: dict = {}

    @property
    def cls(self) -> type:
        return self._cls

    @property
    def cs(self) -> ClassSpec:
        return self._cs

    def __getitem__(self, ty: type[T]) -> T:
        try:
            return self._items[ty]
        except KeyError:
            pass

        fac = self._item_factories[ty]
        ret = fac(self)
        self._items[ty] = ret
        return ret

    def option(self, ty: type[ProcessingOptionT]) -> ProcessingOptionT | None:
        return self._options_dct.get(ty)


##


class Processor(lang.Abstract):
    def __init__(self, ctx: ProcessingContext) -> None:
        super().__init__()

        self._ctx = ctx

    def check(self) -> None:
        pass

    def process(self, cls: type) -> type:
        return cls
