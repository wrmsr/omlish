import typing as ta


##


class LazyGlobals:
    def __init__(
            self,
            *,
            globals: ta.MutableMapping[str, ta.Any] | None = None,  # noqa
            update_globals: bool = False,
    ) -> None:
        super().__init__()

        self._globals = globals
        self._update_globals = update_globals

        self._attr_fns: dict[str, ta.Callable[[], ta.Any]] = {}

    @classmethod
    def install(cls, globals: ta.MutableMapping[str, ta.Any]) -> 'LazyGlobals':  # noqa
        try:
            xga = globals['__getattr__']
        except KeyError:
            pass
        else:
            if not isinstance(xga, cls):
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

    def get(self, attr: str) -> ta.Any:
        try:
            fn = self._attr_fns[attr]
        except KeyError:
            raise AttributeError(attr) from None

        val = fn()

        if self._update_globals and self._globals is not None:
            self._globals[attr] = val

        return val

    def __call__(self, attr: str) -> ta.Any:
        return self.get(attr)
