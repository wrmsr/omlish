import builtins
import contextlib
import functools
import types
import typing as ta


##


class ImportCaptureError(Exception):
    pass


class ImportCaptureErrors:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    class HookError(ImportCaptureError):
        pass

    class AttrError(ImportCaptureError):
        def __init__(self, module: str | None, name: str) -> None:
            super().__init__()

            self.module = module
            self.name = name

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}(module={self.module!r}, name={self.name!r})'

    class ImportError(ImportCaptureError):  # noqa
        def __init__(self, module: str, from_list: ta.Sequence[str] | None) -> None:
            super().__init__()

            self.module = module
            self.from_list = from_list

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}(module={self.module!r}, from_list={self.from_list!r})'

    class ImportStarForbiddenError(ImportError):
        pass

    class UncapturedImportForbiddenError(ImportError):
        pass

    class UnreferencedImportsError(ImportCaptureError):
        def __init__(self, unreferenced: ta.Mapping[str, ta.Sequence[str | None]]) -> None:
            super().__init__()

            self.unreferenced = unreferenced

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}(unreferenced={self.unreferenced!r})'

    class CaptureInProgressError(ImportCaptureError):
        pass


##


class _ImportCaptureHook:
    class ModuleSpec(ta.NamedTuple):
        name: str
        level: int

        def __str__(self) -> str:
            return f'{"." * self.level}{self.name}'

        def __repr__(self) -> str:
            return repr(str(self))

    def __init__(
            self,
            *,
            forbid_uncaptured_imports: bool = False,
    ) -> None:
        super().__init__()

        self._forbid_uncaptured_imports = forbid_uncaptured_imports

        self._modules_by_spec: dict[_ImportCaptureHook.ModuleSpec, _ImportCaptureHook._Module] = {}
        self._modules_by_module_obj: dict[types.ModuleType, _ImportCaptureHook._Module] = {}

        self._attrs: dict[_ImportCaptureHook._ModuleAttr, tuple[_ImportCaptureHook._Module, str]] = {}

    #

    class _ModuleAttr:
        def __init__(
                self,
                module: '_ImportCaptureHook._Module',
                name: str,
        ) -> None:
            super().__init__()

            self.__module = module
            self.__name = name

        def __repr__(self) -> str:
            return f'<{self.__class__.__name__}: {f"{self.__module.spec}:{self.__name}"!r}>'

    class _Module:
        def __init__(
                self,
                spec: '_ImportCaptureHook.ModuleSpec',
                *,
                getattr_handler: ta.Callable[['_ImportCaptureHook._Module', str], ta.Any] | None = None,
        ) -> None:
            super().__init__()

            self.spec = spec

            self.module_obj = types.ModuleType(f'<{self.__class__.__qualname__}: {spec!r}>')
            if getattr_handler is not None:
                self.module_obj.__getattr__ = functools.partial(getattr_handler, self)  # type: ignore[method-assign]  # noqa
            self.initial_module_dict = dict(self.module_obj.__dict__)

            self.contents: dict[str, _ImportCaptureHook._ModuleAttr | types.ModuleType] = {}
            self.imported_whole = False

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({self.spec!r})'

    def _get_or_make_module(self, spec: ModuleSpec) -> _Module:
        try:
            return self._modules_by_spec[spec]
        except KeyError:
            pass

        module = self._Module(
            spec,
            getattr_handler=self._handle_module_getattr,
        )
        self._modules_by_spec[spec] = module
        self._modules_by_module_obj[module.module_obj] = module
        return module

    def _handle_module_getattr(self, module: _Module, attr: str) -> ta.Any:
        if attr in module.contents:
            raise ImportCaptureErrors.AttrError(str(module.spec), attr)

        v: _ImportCaptureHook._ModuleAttr | types.ModuleType
        if not module.spec.name:
            if not module.spec.level:
                raise ImportCaptureError
            cs = _ImportCaptureHook.ModuleSpec(attr, module.spec.level)
            cm = self._get_or_make_module(cs)
            cm.imported_whole = True
            v = cm.module_obj

        else:
            ma = _ImportCaptureHook._ModuleAttr(module, attr)
            self._attrs[ma] = (module, attr)
            v = ma

        module.contents[attr] = v
        setattr(module.module_obj, attr, v)
        return v

    def _handle_import(
            self,
            module: _Module,
            *,
            from_list: ta.Sequence[str] | None,
    ) -> None:
        if from_list is None:
            if module.spec.level or not module.spec.name:
                raise ImportCaptureError

            module.imported_whole = True

        else:
            for attr in from_list:
                if attr == '*':
                    raise ImportCaptureErrors.ImportStarForbiddenError(str(module.spec), from_list)

                x = getattr(module.module_obj, attr)

                bad = False
                if x is not module.contents.get(attr):
                    bad = True
                if isinstance(x, _ImportCaptureHook._ModuleAttr):
                    if self._attrs[x] != (module, attr):
                        bad = True
                elif isinstance(x, types.ModuleType):
                    if x not in self._modules_by_module_obj:
                        bad = True
                else:
                    bad = True
                if bad:
                    raise ImportCaptureErrors.AttrError(str(module.spec), attr)

    #

    _MOD_SELF_ATTR: ta.ClassVar[str] = '__import_capture__'

    def _intercept_import(
            self,
            name: str,
            *,
            globals: ta.Mapping[str, ta.Any] | None = None,  # noqa
            from_list: ta.Sequence[str] | None = None,
            level: int = 0,
    ) -> types.ModuleType | None:
        if not (
                globals is not None and
                globals.get(self._MOD_SELF_ATTR) is self
        ):
            return None

        spec = _ImportCaptureHook.ModuleSpec(name, level)
        module = self._get_or_make_module(spec)

        self._handle_import(
            module,
            from_list=from_list,
        )

        return module.module_obj

    # @abc.abstractmethod
    def hook_context(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> ta.ContextManager[None]:
        raise NotImplementedError

    #

    def verify_state(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> None:
        for m in self._modules_by_spec.values():
            for a, o in m.module_obj.__dict__.items():
                try:
                    i = m.initial_module_dict[a]

                except KeyError:
                    if o is not m.contents[a]:
                        raise ImportCaptureErrors.AttrError(str(m.spec), a) from None

                else:
                    if o != i:
                        raise ImportCaptureErrors.AttrError(str(m.spec), a)

    #

    def build_captured(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
            *,
            collect_unreferenced: bool = False,
    ) -> 'ImportCapture.Captured':
        dct: dict[_ImportCaptureHook._Module, list[tuple[str | None, str]]] = {}

        rem_whole_mods: set[_ImportCaptureHook._Module] = set()
        rem_mod_attrs: set[_ImportCaptureHook._ModuleAttr] = set()
        if collect_unreferenced:
            rem_whole_mods.update([m for m in self._modules_by_spec.values() if m.imported_whole])
            rem_mod_attrs.update(self._attrs)

        for attr, obj in mod_globals.items():
            if isinstance(obj, _ImportCaptureHook._ModuleAttr):
                try:
                    m, a = self._attrs[obj]
                except KeyError:
                    raise ImportCaptureErrors.AttrError(None, attr) from None
                dct.setdefault(m, []).append((a, attr))
                rem_mod_attrs.discard(obj)

            elif isinstance(obj, _ImportCaptureHook._Module):
                raise ImportCaptureErrors.AttrError(None, attr) from None

            elif isinstance(obj, types.ModuleType):
                try:
                    m = self._modules_by_module_obj[obj]
                except KeyError:
                    continue
                if not m.imported_whole:
                    raise RuntimeError(f'ImportCapture module {m.spec!r} not imported_whole')
                dct.setdefault(m, []).append((None, attr))
                rem_whole_mods.discard(m)

        lst: list[ImportCapture.Import] = []
        for m, ts in dct.items():
            if not m.spec.name:
                if not m.spec.level:
                    raise ImportCaptureError
                for imp_attr, as_attr in ts:
                    if not imp_attr:
                        raise RuntimeError
                    lst.append(ImportCapture.Import(
                        '.' * m.spec.level + imp_attr,
                        [(None, as_attr)],
                    ))

            else:
                lst.append(ImportCapture.Import(
                    str(m.spec),
                    ts,
                ))

        unreferenced: dict[str, list[str | None]] | None = None
        if collect_unreferenced and (rem_whole_mods or rem_mod_attrs):
            unreferenced = {}
            for m in rem_whole_mods:
                unreferenced.setdefault(str(m.spec), []).append(None)
            for ma in rem_mod_attrs:
                m, a = self._attrs[ma]
                unreferenced.setdefault(str(m.spec), []).append(a)

        return ImportCapture.Captured(
            lst,
            unreferenced,
        )


class _GlobalBuiltinImportCaptureHook(_ImportCaptureHook):
    @contextlib.contextmanager
    def hook_context(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> ta.Iterator[None]:
        if self._MOD_SELF_ATTR in mod_globals:
            raise ImportCaptureErrors.HookError

        old_import = builtins.__import__

        def new_import(
                name,
                globals=None,  # noqa
                locals=None,  # noqa
                fromlist=None,
                level=0,
        ):
            if (im := self._intercept_import(
                    name,
                    globals=globals,
                    from_list=fromlist,
                    level=level,
            )) is not None:
                return im

            if self._forbid_uncaptured_imports:
                raise ImportCaptureErrors.UncapturedImportForbiddenError(
                    str(_ImportCaptureHook.ModuleSpec(name, level)),
                    fromlist,
                )

            return old_import(
                name,
                globals=globals,
                locals=locals,
                fromlist=fromlist,
                level=level,
            )

        #

        mod_globals[self._MOD_SELF_ATTR] = self
        builtins.__import__ = new_import

        try:
            yield

        finally:
            if not (
                    mod_globals[self._MOD_SELF_ATTR] is self and
                    builtins.__import__ is new_import
            ):
                raise ImportCaptureErrors.HookError

            del mod_globals[self._MOD_SELF_ATTR]
            builtins.__import__ = old_import


##


class ImportCapture:
    class Import(ta.NamedTuple):
        spec: str
        attrs: ta.Sequence[tuple[str | None, str]]

    class Captured(ta.NamedTuple):
        imports: ta.Sequence['ImportCapture.Import']
        unreferenced: ta.Mapping[str, ta.Sequence[str | None]] | None

        @property
        def attrs(self) -> ta.Iterator[str]:
            for pi in self.imports:
                for _, a in pi.attrs:
                    yield a

    #

    def __init__(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],
            *,
            disable: bool = False,
    ) -> None:
        super().__init__()

        self._mod_globals = mod_globals

        self._disabled = disable

    @property
    def disabled(self) -> bool:
        return self._disabled

    #

    class _Result(ta.NamedTuple):
        captured: 'ImportCapture.Captured'

    _result_: _Result | None = None

    @property
    def _result(self) -> _Result:
        if (rs := self._result_) is None:
            raise ImportCaptureErrors.CaptureInProgressError
        return rs

    @property
    def is_complete(self) -> bool:
        return self._result_ is not None

    @property
    def captured(self) -> Captured:
        return self._result.captured

    #

    @contextlib.contextmanager
    def capture(
            self,
            *,
            unreferenced_callback: ta.Callable[[ta.Mapping[str, ta.Sequence[str | None]]], None] | None = None,
            raise_unreferenced: bool = False,
    ) -> ta.Iterator[ta.Self]:
        if self._result_ is not None:
            raise ImportCaptureError('capture already complete')

        if self._disabled:
            self._result_ = ImportCapture._Result(
                ImportCapture.Captured(
                    [],
                    None,
                ),
            )
            yield self
            return

        hook = _GlobalBuiltinImportCaptureHook()

        with hook.hook_context(self._mod_globals):
            yield self

        hook.verify_state(self._mod_globals)

        blt = hook.build_captured(
            self._mod_globals,
            collect_unreferenced=unreferenced_callback is not None or raise_unreferenced,
        )

        if blt.unreferenced:
            if unreferenced_callback:
                unreferenced_callback(blt.unreferenced)
            if raise_unreferenced:
                raise ImportCaptureErrors.UnreferencedImportsError(blt.unreferenced)

        for pi in blt.imports:
            for _, a in pi.attrs:
                del self._mod_globals[a]

        self._result_ = ImportCapture._Result(
            blt,
        )

    #

    def update_exports(self) -> None:
        cap = self._result.captured

        try:
            al: ta.Any = self._mod_globals['__all__']
        except KeyError:
            al = self._mod_globals['__all__'] = [k for k in self._mod_globals if not k.startswith('_')]
        else:
            if not isinstance(al, ta.MutableSequence):
                al = self._mod_globals['__all__'] = list(al)

        al_s = set(al)
        for a in cap.attrs:
            if a not in al_s:
                al.append(a)
                al_s.add(a)
