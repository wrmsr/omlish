"""
Insufficient alt impls:
 - `sys.meta_path`:
  - need access to the `fromlist` and `level` arguments passed to `__import__`
  - need to return fake modules to the import operation which are not added to `sys.modules`
 - `sys.addaudithook`: cannot prevent import or inject result
 - `sys.settrace` / bytecode tracing: same
 - jit bytecode rewriting: slower than just importing everything

Possible alt impls:
 - aot static analysis, codegen, compare, if valid skip ctxmgr body and inject proxies, otherwise warn and run
  - or just gen code inline, if ta.TYPE_CHECKING: .... else: # @omlish-generate-auto-proxy-import/init
   - generate classic `foo = _lang.proxy_import('.foo', __package__)` blocks
"""
import builtins
import contextlib
import functools
import importlib.util
import sys
import threading
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
        def __init__(
                self,
                name: str,
                *,
                level: int | None = None,
                from_list: ta.Sequence[str] | None,
        ) -> None:
            super().__init__()

            self.name = name
            self.level = level
            self.from_list = from_list

        def __repr__(self) -> str:
            return ''.join([
                f'{self.__class__.__qualname__}(',
                f'name={self.name!r}',
                *([f', level={self.level!r}'] if self.level is not None else []),
                *([f', from_list={self.from_list!r}'] if self.from_list is not None else []),
                ')',
            ])

    class ImportStarForbiddenError(ImportError):
        pass

    class UncapturedImportForbiddenError(ImportError):
        pass

    class UnreferencedImportsError(ImportCaptureError):
        def __init__(self, unreferenced: ta.Sequence[str]) -> None:
            super().__init__()

            self.unreferenced = unreferenced

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}(unreferenced={self.unreferenced!r})'

    class CaptureInProgressError(ImportCaptureError):
        pass


##


class _ImportCaptureHook:
    def __init__(
            self,
            *,
            package: str | None = None,
            forbid_uncaptured_imports: bool = False,
    ) -> None:
        super().__init__()

        self._package = package
        self._forbid_uncaptured_imports = forbid_uncaptured_imports

        self._modules_by_name: dict[str, _ImportCaptureHook._Module] = {}
        self._modules_by_module_obj: dict[types.ModuleType, _ImportCaptureHook._Module] = {}

    #

    class _Module:
        def __init__(
                self,
                name: str,
                getattr_handler: ta.Callable[['_ImportCaptureHook._Module', str], ta.Any],
                *,
                parent: ta.Optional['_ImportCaptureHook._Module'] = None,
        ) -> None:
            super().__init__()

            if name.startswith('.'):
                raise ImportCaptureError

            self.name = name
            self.parent = parent

            self.base_name = name.rpartition('.')[2]
            self.root: _ImportCaptureHook._Module = parent.root if parent is not None else self  # noqa

            self.children: dict[str, _ImportCaptureHook._Module] = {}
            self.descendants: set[_ImportCaptureHook._Module] = set()

            self.module_obj = types.ModuleType(f'<{self.__class__.__qualname__}: {name}>')
            self.module_obj.__file__ = None
            self.module_obj.__getattr__ = functools.partial(getattr_handler, self)  # type: ignore[method-assign]  # noqa
            self.initial_module_dict = dict(self.module_obj.__dict__)

            self.explicit = False
            self.immediate = False

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}<{self.name}{"!" if self.immediate else "+" if self.explicit else ""}>'

        def set_explicit(self) -> None:
            cur: _ImportCaptureHook._Module | None = self
            while cur is not None and not cur.explicit:
                cur.explicit = True
                cur = cur.parent

    #

    @property
    def _modules(self) -> ta.Sequence[_Module]:
        return sorted(self._modules_by_name.values(), key=lambda m: m.name)

    def _get_or_make_module(self, name: str) -> _Module:
        try:
            return self._modules_by_name[name]
        except KeyError:
            pass

        parent: _ImportCaptureHook._Module | None = None
        if '.' in name:
            rest, _, attr = name.rpartition('.')
            parent = self._get_or_make_module(rest)
            if attr in parent.children:
                raise ImportCaptureErrors.AttrError(rest, attr)

        module = _ImportCaptureHook._Module(
            name,
            self._handle_module_getattr,
            parent=parent,
        )
        self._modules_by_name[name] = module
        self._modules_by_module_obj[module.module_obj] = module

        if parent is not None:
            parent.children[module.base_name] = module
            setattr(parent.module_obj, module.base_name, module.module_obj)
            parent.root.descendants.add(module)

        return module

    def _make_child_module(self, module: _Module, attr: str) -> _Module:
        if attr in module.children:
            raise ImportCaptureErrors.AttrError(module.name, attr)

        return self._get_or_make_module(f'{module.name}.{attr}')

    #

    def _handle_module_getattr(self, module: _Module, attr: str) -> ta.Any:
        if not module.explicit:
            raise ImportCaptureErrors.AttrError(module.name, attr)

        return self._make_child_module(module, attr).module_obj

    def _handle_import(
            self,
            name: str,
            *,
            from_list: ta.Sequence[str] | None,
    ) -> types.ModuleType:
        module = self._get_or_make_module(name)

        if from_list is None:
            module.set_explicit()
            module.root.immediate = True
            return module.root.module_obj

        else:
            for attr in from_list:
                if attr == '*':
                    raise ImportCaptureErrors.ImportStarForbiddenError(module.name, from_list=from_list)

                if (cm := module.children.get(attr)) is None:
                    cm = self._make_child_module(module, attr)
                    cm.set_explicit()
                    cm.immediate = True
                    continue

                x = getattr(module.module_obj, attr)
                if x is not cm.module_obj or x not in self._modules_by_module_obj:
                    raise ImportCaptureErrors.AttrError(module.name, attr)

            return module.module_obj

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

        if level:
            if not self._package:
                raise ImportCaptureError
            name = importlib.util.resolve_name(('.' * level) + name, self._package)

        return self._handle_import(
            name,
            from_list=from_list,
        )

    @ta.final
    @contextlib.contextmanager
    def hook_context(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> ta.Iterator[None]:
        if self._MOD_SELF_ATTR in mod_globals:
            raise ImportCaptureErrors.HookError

        mod_globals[self._MOD_SELF_ATTR] = self

        try:
            with self._hook_context(mod_globals):
                yield

        finally:
            if mod_globals[self._MOD_SELF_ATTR] is not self:
                raise ImportCaptureErrors.HookError

            del mod_globals[self._MOD_SELF_ATTR]

    # @abc.abstractmethod
    def _hook_context(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> ta.ContextManager[None]:
        raise NotImplementedError

    #

    def verify_state(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> None:
        for m in self._modules_by_name.values():
            if m.immediate and not m.explicit:
                raise ImportCaptureError

            if not m.explicit and m.children:
                raise ImportCaptureError

            for a, o in m.module_obj.__dict__.items():
                try:
                    i = m.initial_module_dict[a]

                except KeyError:
                    if o is not m.children[a].module_obj:
                        raise ImportCaptureErrors.AttrError(m.name, a) from None

                else:
                    if o != i:
                        raise ImportCaptureErrors.AttrError(m.name, a)

    #

    def build_captured(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
            *,
            collect_unreferenced: bool = False,
    ) -> 'ImportCapture.Captured':
        rem_explicit_mods: set[_ImportCaptureHook._Module] = set()
        if collect_unreferenced:
            rem_explicit_mods.update(
                m for m in self._modules_by_name.values()
                if m.immediate
                and m.parent is not None  # No good way to tell if user did `import a.b.c` or `import a.b.c as c`
            )

        #

        dct: dict[_ImportCaptureHook._Module, list[tuple[str | None, str]]] = {}

        for attr, obj in mod_globals.items():
            if isinstance(obj, _ImportCaptureHook._Module):
                raise ImportCaptureErrors.AttrError(None, attr) from None

            elif isinstance(obj, types.ModuleType):
                try:
                    m = self._modules_by_module_obj[obj]
                except KeyError:
                    continue

                if m.explicit:
                    dct.setdefault(m, []).append((None, attr))
                    if m in rem_explicit_mods:
                        # Remove everything reachable from this root *except* items imported immediately, such as
                        # `from x import y` - those still need to be immediately reachable.
                        rem_explicit_mods -= {dm for dm in m.descendants if not dm.immediate}
                        rem_explicit_mods.remove(m)

                else:
                    p = m.parent
                    if p is None or not p.explicit:
                        raise ImportCaptureError
                    dct.setdefault(p, []).append((m.base_name, attr))

        #

        mods: dict[str, ImportCapture.Module] = {}

        def build_import_module(m: _ImportCaptureHook._Module) -> ImportCapture.Module:
            children: dict[str, ImportCapture.Module] = {}
            attrs: list[str] = []
            for cm in sorted(m.children.values(), key=lambda cm: cm.name):
                if not cm.explicit:
                    attrs.append(cm.base_name)
                else:
                    children[cm.base_name] = build_import_module(cm)

            mod = ImportCapture.Module(
                m.name,
                children or None,
                attrs or None,
            )

            if m.parent is None:
                mod.parent = None
            for c in children.values():
                c.parent = mod

            mods[mod.name] = mod
            return mod

        root_mods: dict[str, ImportCapture.Module] = {
            m.base_name: build_import_module(m)
            for m in self._modules_by_name.values()
            if m.parent is None
        }

        mods = dict(sorted(mods.items(), key=lambda t: t[0]))
        root_mods = dict(sorted(root_mods.items(), key=lambda t: t[0]))

        #

        imps: list[ImportCapture.Import] = []

        for m, ts in sorted(dct.items(), key=lambda t: t[0].name):
            imps.append(ImportCapture.Import(
                mods[m.name],
                [r for l, r in ts if l is None] or None,
                [(l, r) for l, r in ts if l is not None] or None,
            ))

        #

        unreferenced: list[str] | None = None
        if collect_unreferenced and rem_explicit_mods:
            unreferenced = sorted(m.name for m in rem_explicit_mods)

        return ImportCapture.Captured(
            {i.module.name: i for i in imps},

            mods,
            root_mods,

            unreferenced,
        )


#


class _AbstractBuiltinsImportCaptureHook(_ImportCaptureHook):
    def __init__(
            self,
            *,
            _frame: types.FrameType | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

    def _new_import(
            self,
            old_import,
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
                name,
                level=level,
                from_list=fromlist,
            )

        return old_import(
            name,
            globals=globals,
            locals=locals,
            fromlist=fromlist,
            level=level,
        )


#


class _UnsafeGlobalBuiltinsImportCaptureHook(_AbstractBuiltinsImportCaptureHook):
    @contextlib.contextmanager
    def _hook_context(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> ta.Iterator[None]:
        old_import = builtins.__import__
        new_import = functools.partial(self._new_import, old_import)

        builtins.__import__ = new_import

        try:
            yield

        finally:
            if builtins.__import__ is not new_import:
                raise ImportCaptureErrors.HookError

            builtins.__import__ = old_import


class _SomewhatThreadSafeGlobalBuiltinsImportCaptureHook(_AbstractBuiltinsImportCaptureHook):
    class _AlreadyPatchedError(Exception):
        pass

    @ta.final
    class _Patch:
        __lock: ta.ClassVar[threading.Lock] = threading.Lock()

        def __init__(self, old_import):
            self.__old_import = old_import
            self.__hooks = {}
            self.__uninstalled = False

        @classmethod
        def _add_hook(cls, mod_globals, new_import) -> '_SomewhatThreadSafeGlobalBuiltinsImportCaptureHook._Patch':
            gi = id(mod_globals)
            for _ in range(1_000):
                try:
                    with cls.__lock:
                        x: ta.Any = builtins.__import__
                        p: _SomewhatThreadSafeGlobalBuiltinsImportCaptureHook._Patch
                        if x.__class__ is cls:
                            p = x
                            if p.__uninstalled:  # noqa
                                raise _SomewhatThreadSafeGlobalBuiltinsImportCaptureHook._AlreadyPatchedError  # noqa
                        else:
                            p = cls(x)
                            builtins.__import__ = p
                        p.__hooks[gi] = (mod_globals, new_import)
                        return p
                except _SomewhatThreadSafeGlobalBuiltinsImportCaptureHook._AlreadyPatchedError:
                    pass
            raise ImportCaptureErrors.HookError('Failed to install builtins hook')

        def _remove_hook(self, mod_globals, *, no_raise=False):
            gi = id(mod_globals)
            with self.__lock:
                tg, _ = self.__hooks[gi]
                del self.__hooks[gi]
                if not self.__uninstalled and not self.__hooks:
                    self.__uninstalled = True
                    if builtins.__import__ is not self:
                        if not no_raise:
                            # TODO: warn?
                            raise ImportCaptureErrors.HookError('Unexpected builtins hook')
                    else:
                        builtins.__import__ = self.__old_import
                if tg is not mod_globals:
                    if not no_raise:
                        # TODO: warn?
                        raise ImportCaptureErrors.HookError('Mismatched globals')

        def __call__(
                self,
                name,
                globals=None,  # noqa
                locals=None,  # noqa
                fromlist=None,
                level=0,
        ):
            if globals is not None and (tup := self.__hooks.get(id(globals))) is not None:
                tg, tf = tup
                if tg is globals:
                    return tf(
                        self.__old_import,
                        name,
                        globals=globals,
                        locals=locals,
                        fromlist=fromlist,
                        level=level,
                    )
                else:
                    self._remove_hook(tg, no_raise=True)

            return self.__old_import(
                name,
                globals=globals,
                locals=locals,
                fromlist=fromlist,
                level=level,
            )

    @contextlib.contextmanager
    def _hook_context(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> ta.Iterator[None]:
        patch = _SomewhatThreadSafeGlobalBuiltinsImportCaptureHook._Patch._add_hook(mod_globals, self._new_import)  # noqa

        try:
            yield

        finally:
            patch._remove_hook(mod_globals)  # noqa


#


_cext_: ta.Any


def _cext() -> ta.Any:
    global _cext_
    try:
        return _cext_
    except NameError:
        pass

    cext: ta.Any
    try:
        from . import _capture as cext  # type: ignore
    except ImportError:
        cext = None

    _cext_ = cext
    return cext


class _FrameBuiltinsImportCaptureHook(_AbstractBuiltinsImportCaptureHook):
    def __init__(
            self,
            *,
            _frame: types.FrameType,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._frame = _frame

    @classmethod
    def _set_frame_builtins(
            cls,
            frame: types.FrameType,
            new_builtins: dict[str, ta.Any],
    ) -> bool:
        return _cext()._set_frame_builtins(frame, frame.f_builtins, new_builtins)  # noqa

    @contextlib.contextmanager
    def _hook_context(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
    ) -> ta.Iterator[None]:
        old_builtins = self._frame.f_builtins
        old_import = old_builtins['__import__']
        new_import = functools.partial(self._new_import, old_import)

        new_builtins = dict(old_builtins)
        new_builtins['__import__'] = new_import
        if not self._set_frame_builtins(self._frame, new_builtins):
            raise ImportCaptureErrors.HookError

        try:
            yield

        finally:
            if self._frame.f_builtins is not new_builtins:
                raise ImportCaptureErrors.HookError

            if not self._set_frame_builtins(self._frame, old_builtins):
                raise ImportCaptureErrors.HookError


#


_CAPTURE_IMPLS: ta.Mapping[str, type[_AbstractBuiltinsImportCaptureHook]] = {
    'cext': _FrameBuiltinsImportCaptureHook,
    'somewhat_safe': _SomewhatThreadSafeGlobalBuiltinsImportCaptureHook,
    'unsafe': _UnsafeGlobalBuiltinsImportCaptureHook,
}


def _new_import_capture_hook(
        mod_globals: ta.MutableMapping[str, ta.Any],  # noqa
        *,
        stack_offset: int = 0,
        capture_impl: str | None = None,
        **kwargs: ta.Any,
) -> '_ImportCaptureHook':
    if '_frame' not in kwargs:
        frame: types.FrameType | None = sys._getframe(1 + stack_offset)  # noqa
        if frame is None or frame.f_globals is not mod_globals:
            raise ImportCaptureError("Can't find importing frame")
        kwargs['_frame'] = frame

    kwargs.setdefault('package', mod_globals.get('__package__'))

    cls: type[_AbstractBuiltinsImportCaptureHook]
    if capture_impl is not None:
        cls = _CAPTURE_IMPLS[capture_impl]
    elif _cext() is not None:
        cls = _FrameBuiltinsImportCaptureHook
    else:
        cls = _SomewhatThreadSafeGlobalBuiltinsImportCaptureHook

    return cls(**kwargs)


##


ImportCaptureModuleKind: ta.TypeAlias = ta.Literal[
    'parent',
    'terminal',
    'leaf',
]


class ImportCapture:
    @ta.final
    class Module:
        def __init__(
                self,
                name: str,
                children: ta.Mapping[str, 'ImportCapture.Module'] | None = None,
                attrs: ta.Sequence[str] | None = None,
        ) -> None:
            self.name = name
            self.children = children
            self.attrs = attrs

            self.base_name = name.rpartition('.')[2]

            if not self.children and not self.attrs:
                self.kind = 'leaf'
            elif not self.children or all(c.kind == 'leaf' for c in self.children.values()):
                self.kind = 'terminal'
            else:
                self.kind = 'parent'

        parent: ta.Optional['ImportCapture.Module']

        kind: ImportCaptureModuleKind

        def __repr__(self) -> str:
            return ''.join([
                f'{self.__class__.__name__}(',
                f'{self.name!r}',
                f', :{self.kind}',
                *([f', children=[{", ".join(map(repr, self.children))}]'] if self.children else []),
                *([f', attrs={self.attrs!r}'] if self.attrs else []),
                ')',
            ])

        _root: 'ImportCapture.Module'

        @property
        def root(self) -> 'ImportCapture.Module':
            try:
                return self._root
            except AttributeError:
                pass

            root = self
            while root.parent is not None:
                root = root.parent
            self._root = root
            return root

    @ta.final
    class Import:
        def __init__(
                self,
                module: 'ImportCapture.Module',
                as_: ta.Sequence[str] | None,
                attrs: ta.Sequence[tuple[str, str]] | None,  # ('foo', 'bar') -> `import foo as bar` - explicitly not a dict  # noqa
        ) -> None:
            self.module = module
            self.as_ = as_
            self.attrs = attrs

        def __repr__(self) -> str:
            return ''.join([
                f'{self.__class__.__name__}(',
                f'{self.module.name!r}',
                *([f', as_={self.as_!r}'] if self.as_ else []),
                *([f', attrs={self.attrs!r}'] if self.attrs else []),
                ')',
            ])

    @ta.final
    class Captured:
        def __init__(
                self,

                imports: ta.Mapping[str, 'ImportCapture.Import'],

                modules: ta.Mapping[str, 'ImportCapture.Module'],
                root_modules: ta.Mapping[str, 'ImportCapture.Module'],

                unreferenced: ta.Sequence[str] | None,
        ) -> None:
            self.imports = imports

            self.modules = modules
            self.root_modules = root_modules

            self.unreferenced = unreferenced

        @property
        def attrs(self) -> ta.Iterator[str]:
            for pi in self.imports.values():
                if pi.as_:
                    yield from pi.as_
                if pi.attrs:
                    for _, a in pi.attrs:
                        yield a

    EMPTY_CAPTURED: ta.ClassVar[Captured] = Captured(
        {},
        {},
        {},
        None,
    )

    #

    def __init__(
            self,
            mod_globals: ta.MutableMapping[str, ta.Any],
            *,
            _hook: _ImportCaptureHook,

            disable: bool = False,
    ) -> None:
        super().__init__()

        self._mod_globals = mod_globals
        self._hook = _hook

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
            unreferenced_callback: ta.Callable[[ta.Sequence[str]], None] | None = None,
            raise_unreferenced: bool = False,
    ) -> ta.Iterator[ta.Self]:
        if self._result_ is not None:
            raise ImportCaptureError('capture already complete')

        if self._disabled:
            self._result_ = ImportCapture._Result(
                ImportCapture.EMPTY_CAPTURED,
            )
            yield self
            return

        with self._hook.hook_context(self._mod_globals):
            yield self

        self._hook.verify_state(self._mod_globals)

        blt = self._hook.build_captured(
            self._mod_globals,
            collect_unreferenced=unreferenced_callback is not None or raise_unreferenced,
        )

        if blt.unreferenced:
            if unreferenced_callback:
                unreferenced_callback(blt.unreferenced)
            if raise_unreferenced:
                raise ImportCaptureErrors.UnreferencedImportsError(blt.unreferenced)

        for a in blt.attrs:
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
