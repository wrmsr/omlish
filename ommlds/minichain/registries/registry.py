# ruff: noqa: SLF001
"""
TODO:
 - rename to TypeRegistry
 - queue register_types + late load manifests ? less urgent than late loading marshal lol
"""
import sys
import threading
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl

from .manifests import RegistryManifest
from .manifests import RegistryTypeManifest


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


@ta.final
class RegistryTypeName(dc.Box[str], lang.Final):
    pass


##


class Registry:
    def __init__(
            self,
            registry_type_manifests: ta.Iterable[RegistryTypeManifest],
            registry_manifests: ta.Iterable[RegistryManifest],
    ) -> None:
        super().__init__()

        self._lock = threading.RLock()

        self._registry_type_manifests = list(registry_type_manifests)
        self._registry_manifests = list(registry_manifests)

        entries_by_name_by_type: dict[str, dict[str, Registry.Entry]] = {}
        for rm in self._registry_manifests:
            e = self.Entry(_rm=rm)
            ed = entries_by_name_by_type.setdefault(rm.type, {})
            for n in (rm.name, *(rm.aliases or ())):
                check.not_in(n, ed)
                ed[n] = e

        self._types_by_name: dict[str, Registry.Type] = {}
        self._types_by_cls: dict[ta.Any, Registry.Type] = {}
        self._types_by_rty: dict[rfl.Type, Registry.Type] = {}

        for rtm in self._registry_type_manifests:
            check.not_in(rtm.attr, self._types_by_name)

            rt = self.Type(
                _o=self,

                _rtm=rtm,
                _entries=entries_by_name_by_type.get(rtm.attr, {}),

                _name=rtm.attr,
                _module=rtm.module,
            )

            self._types_by_name[rtm.attr] = rt

    #

    class Entry:
        def __init__(
                self,
                *,
                _rm: RegistryManifest,
        ) -> None:
            super().__init__()

            self._rm = _rm

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({self.name!r})'

        @property
        def name(self) -> str:
            return self._rm.name

        _resolved: ta.Any

        def resolve(self) -> ta.Any:
            try:
                return self._resolved
            except AttributeError:
                pass
            self._resolved = resolved = self._rm.resolve()
            return resolved

    #

    class Type:
        def __init__(
                self,
                *,
                _o: Registry,

                _rtm: RegistryTypeManifest | None = None,
                _entries: ta.Mapping[str, Registry.Entry] | None = None,

                _name: str | None = None,
                _module: str | None = None,

                _has_registered: bool = False,
        ) -> None:
            super().__init__()

            self._o: ta.Final = _o

            self._rtm: ta.Final = _rtm
            self._entries: ta.Final = _entries or {}

            self._name: ta.Final = _name
            self._module: ta.Final = _module

            self._has_registered = _has_registered

        __repr__: ta.Any = lang.AttrOps(
            'name',
            'module',
            repr_filter=lang.is_not_none,
        ).repr

        @property
        def name(self) -> str | None:
            return self._name

        @property
        def module(self) -> str | None:
            return self._module

        @property
        def entries(self) -> ta.Mapping[str, Registry.Entry]:
            return self._entries

        #

        __cls: lang.Maybe[ta.Any] = lang.empty()
        __rty: lang.Maybe[rfl.Type] = lang.empty()
        __named_rty: lang.Maybe[rfl.Type] = lang.empty()

        def _name_rty(self, rty: rfl.Type) -> rfl.Type:
            if self._name is None:
                return rty

            return rfl.add_rfl_annotations(rty, RegistryTypeName(self._name))

        def _maybe_set_cls(self, cls: ta.Any) -> None:
            check.not_none(cls)
            check.not_isinstance(cls, rfl.TypeInfo)

            if self.__cls.present:
                return

            rty = rfl.type_(cls)
            named_rty = self._name_rty(rty)

            check.not_in(cls, self._o._types_by_cls)
            check.not_in(rty, self._o._types_by_rty)
            check.not_in(named_rty, self._o._types_by_rty)

            self._o._types_by_cls[cls] = self
            self._o._types_by_rty[rty] = self
            self._o._types_by_rty[named_rty] = self

            self.__cls = lang.just(cls)
            self.__rty = lang.just(rty)
            self.__named_rty = lang.just(named_rty)

        def cls(self) -> ta.Any:
            if (cls := self.__cls).present:
                return cls.must()

            with self._o._lock:
                if (cls := self.__cls).present:
                    return cls.must()

                cls = check.not_none(self._rtm).resolve()

                self._maybe_set_cls(cls)
                return cls

        def rty(self) -> rfl.Type:
            self.cls()
            return self.__rty.must()

        def named_rty(self) -> rfl.Type:
            self.cls()
            return self.__named_rty.must()

        #

        def lookup(self, name: str) -> ta.Any:
            if not (entries := self._entries):
                raise KeyError(name)

            e = entries[name]
            return e.resolve()

    #

    def register_type(
            self,
            cls: ta.Any,
            *,
            name: str | None = None,
            module: str | None = None,
    ) -> Type:
        check.not_none(cls)
        check.not_isinstance(cls, rfl.TypeInfo)

        with self._lock:
            if (rt := self._types_by_cls.get(cls)) is not None:
                if name is not None:
                    try:
                        nrt = self._types_by_name[name]
                    except KeyError:
                        pass
                    else:
                        if rt is not nrt:
                            raise RuntimeError(f'Type {name!r} already present')

                if rt._has_registered:
                    raise RuntimeError(f'Type {cls} already registered')

                rt._has_registered = True
                rt._maybe_set_cls(cls)
                return rt

            if name is None:
                mo = sys.modules[check.not_none(module)]
                name = check.single(a for a, o in mo.__dict__.items() if o is cls)

            if name is not None:
                if (rt := self._types_by_name.get(name)) is not None:
                    if rt._has_registered:
                        raise RuntimeError(f'Type {name!r} already registered')

                    rt._has_registered = True
                    rt._maybe_set_cls(cls)
                    return rt

            rt = self.Type(
                _o=self,

                _name=name,
                _module=module,

                _has_registered=True,
            )

            if name is not None:
                self._types_by_name[name] = rt

            rt._maybe_set_cls(cls)

        return rt

    def get_type(self, selector: ta.Any) -> Type:
        if isinstance(selector, str):
            return self._types_by_name[selector]
        else:
            return self._types_by_cls[selector]

    #

    def get_type_cls(self, name: str) -> type:
        return self.get_type(name).cls()

    def get_cls(self, selector: ta.Any, name: str) -> type:
        return self.get_type(selector).lookup(name)
