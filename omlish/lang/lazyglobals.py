import threading
import typing as ta


##


class AmbiguousLazyGlobalsFallbackError(Exception):
    def __init__(self, attr: str, fallbacks: list[ta.Callable[[str], ta.Any]]) -> None:
        super().__init__()

        self.attr = attr
        self.fallbacks = fallbacks

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.attr!r}, {self.fallbacks!r})'


_LAZY_GLOBALS_LOCK = threading.RLock()


@ta.final
class LazyGlobals:
    def __init__(
            self,
            *,
            globals: ta.MutableMapping[str, ta.Any] | None = None,  # noqa
            update_globals: bool = False,
    ) -> None:
        self._globals = globals
        self._update_globals = update_globals

        self._attr_fns: dict[str, ta.Callable[[], ta.Any]] = {}
        self._fallback_fns: list[ta.Callable[[str], ta.Callable[[], ta.Any]]] = []

    @classmethod
    def install(cls, globals: ta.MutableMapping[str, ta.Any]) -> 'LazyGlobals':  # noqa
        try:
            xga = globals['__getattr__']
        except KeyError:
            pass
        else:
            if xga.__class__ is not cls:
                raise RuntimeError(f'Module already has __getattr__ hook: {xga}')  # noqa
            return xga

        with _LAZY_GLOBALS_LOCK:
            try:
                xga = globals['__getattr__']
            except KeyError:
                pass
            else:
                if xga.__class__ is not cls:
                    raise RuntimeError(f'Module already has __getattr__ hook: {xga}')  # noqa
                return xga

            lm = cls(
                globals=globals,
                update_globals=True,
            )

            globals['__getattr__'] = lm

            return lm

    def set_fn(self, attr: str, fn: ta.Callable[[], ta.Any]) -> 'LazyGlobals':
        self._attr_fns[attr] = fn
        return self

    def add_fallback_fn(self, fn: ta.Callable[[str], ta.Callable[[], ta.Any]]) -> 'LazyGlobals':
        self._fallback_fns.append(fn)
        return self

    def get(self, attr: str) -> ta.Any:
        val: ta.Any

        if (attr_fn := self._attr_fns.get(attr)) is not None:
            val = attr_fn()

        elif (fallbacks := [(fb_fn, fb_fn(attr)) for fb_fn in self._fallback_fns]):
            if len(fallbacks) > 1:
                raise AmbiguousLazyGlobalsFallbackError(attr, [fb_fn for fb_fn, _ in fallbacks])
            [val] = fallbacks

        else:
            raise AttributeError(attr)

        if self._update_globals and self._globals is not None:
            self._globals[attr] = val

        return val

    def __call__(self, attr: str) -> ta.Any:
        return self.get(attr)
