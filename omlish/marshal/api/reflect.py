import dataclasses as dc
import threading
import typing as ta
import weakref

from ... import lang
from ... import reflect2 as rfl
from ... import typedvalues as tv
from .configs import Config
from .configs import Configs
from .internalstate import InternalState


##


@dc.dataclass(frozen=True)
class ReflectOverride(Config, tv.UniqueTypedValue, lang.Final):
    """
    Substitutes the registered runtime object with `obj` wherever it occurs in an annotation being reflected - at any
    level of nesting. Overrides must be registered before the first reflection through their config registry (in
    practice: during lazy init) - the registry's mirror bakes them in.
    """

    obj: ta.Any


##


def get_rty_config_key(rty: rfl.Type) -> ta.Any | None:
    """The runtime object under which configs applying to this reflected type would have been registered."""

    if (obj := rfl.get_runtime_object_or_none(rty)) is not None:
        return obj

    if isinstance(rty, rfl.TypeAliasType) and (alias := rty.alias) is not None:
        return alias.runtime_object

    return None


##


def _make_context_mirror(configs: Configs) -> rfl.Mirror:
    # The substitutor must not strongly capture the configs - InternalState weakly keys per-registry state, and a
    # mirror (held in that state) strongly referencing its registry would pin the entry forever.
    configs_ref = weakref.ref(configs)

    def substitutor(obj: object) -> object | None:
        if (cfgs := configs_ref()) is None:
            return None

        try:
            cvs = cfgs.get(obj)
        except TypeError:
            # Unhashable runtime annotation objects cannot have been registered as config keys.
            return None

        if (ovr := cvs.get(ReflectOverride)) is not None:
            return ovr.obj

        return None

    from ...reflect2._mirror import MirrorImpl

    return MirrorImpl(
        # parent=rfl.global_root_mirror(),
        reflect_substitutor=substitutor,
    )


class ContextMirrorState(InternalState.ByConfig.Entry, lang.Final):
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.Lock()

    _mirror: rfl.Mirror

    def get_mirror(self, configs: Configs) -> rfl.Mirror:
        try:
            return self._mirror
        except AttributeError:
            pass

        with self._lock:
            try:
                return self._mirror
            except AttributeError:
                pass

            mirror = _make_context_mirror(configs)
            self._mirror = mirror
            return mirror
