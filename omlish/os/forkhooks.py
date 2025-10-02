# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - https://github.com/python/cpython/issues/50970
"""
import os
import threading
import typing as ta

from ..lite.abstract import Abstract
from ..lite.check import check


##


class _ForkHookManager:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    def __init_subclass__(cls, **kwargs):  # noqa
        raise TypeError

    #

    # Intentionally not an RLock - do not nest calls.
    _lock: ta.ClassVar[threading.Lock] = threading.Lock()

    #

    class Hook(ta.NamedTuple):
        key: ta.Any
        priority: int

        # NOTE: these are called inside the global, non-reentrant manager lock
        before_fork: ta.Optional[ta.Callable[[], None]] = None
        after_fork_in_parent: ta.Optional[ta.Callable[[], None]] = None
        after_fork_in_child: ta.Optional[ta.Callable[[], None]] = None

    #

    _hooks_by_key: ta.ClassVar[ta.Dict[ta.Any, Hook]] = {}

    _hook_keys: ta.ClassVar[ta.FrozenSet[ta.Any]] = frozenset()
    _priority_ordered_hooks: ta.ClassVar[ta.List[Hook]] = []

    @classmethod
    def _rebuild_hook_collections(cls) -> None:
        cls._hook_keys = frozenset(cls._hooks_by_key)

        # Uses dict order preservation to retain insertion-order of hooks of equal priority (although that shouldn't be
        # depended upon for usecase correctness).
        cls._priority_ordered_hooks = sorted(cls._hooks_by_key.values(), key=lambda h: h.priority)

    #

    class HookAlreadyPresentError(Exception):
        pass

    @classmethod
    def add_hook(cls, hook: Hook) -> None:
        with cls._lock:
            if hook.key in cls._hooks_by_key:
                raise cls.HookAlreadyPresentError(hook.key)

            check.isinstance(hook.priority, int)

            cls._hooks_by_key[hook.key] = hook
            cls._rebuild_hook_collections()

            cls._install()

    @classmethod
    def try_add_hook(cls, hook: Hook) -> bool:
        if hook.key in cls._hook_keys:
            return False

        try:
            cls.add_hook(hook)
        except cls.HookAlreadyPresentError:
            return False
        else:
            return True

    @classmethod
    def contains_hook(cls, key: ta.Any) -> bool:
        return key in cls._hook_keys

    @classmethod
    def remove_hook(cls, key: ta.Any) -> None:
        with cls._lock:
            del cls._hooks_by_key[key]

            cls._rebuild_hook_collections()

    #

    _installed: ta.ClassVar[bool] = False

    @classmethod
    def _install(cls) -> bool:
        if cls._installed:
            return False

        check.state(not cls._installed)

        os.register_at_fork(
            before=cls._before_fork,
            after_in_parent=cls._after_fork_in_parent,
            after_in_child=cls._after_fork_in_child,
        )

        cls._installed = True
        return True

    @classmethod
    def install(cls) -> bool:
        with cls._lock:
            return cls._install()

    #

    @classmethod
    def _before_fork(cls) -> None:
        cls._lock.acquire()

        for hook in cls._priority_ordered_hooks:
            if (fn := hook.before_fork) is not None:
                fn()

    @classmethod
    def _after_fork_in_parent(cls) -> None:
        for hook in cls._priority_ordered_hooks:
            if (fn := hook.after_fork_in_parent) is not None:
                fn()

        cls._lock.release()

    @classmethod
    def _after_fork_in_child(cls) -> None:
        for hook in cls._priority_ordered_hooks:
            if (fn := hook.after_fork_in_child) is not None:
                fn()

        cls._lock.release()


#


class ForkHook(Abstract):
    @ta.final
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @classmethod
    @ta.final
    def install(cls) -> bool:
        if _ForkHookManager.contains_hook(cls):
            return False

        return _ForkHookManager.try_add_hook(_ForkHookManager.Hook(
            key=cls,
            priority=cls._hook_priority,

            before_fork=cls._before_fork,
            after_fork_in_parent=cls._after_fork_in_parent,
            after_fork_in_child=cls._after_fork_in_child,
        ))

    def __init_subclass__(cls, install: bool = False, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if install:
            cls.install()

    #

    _hook_priority: ta.ClassVar[int] = 0

    @classmethod  # noqa
    def _before_fork(cls) -> None:
        pass

    @classmethod  # noqa
    def _after_fork_in_parent(cls) -> None:
        pass

    @classmethod  # noqa
    def _after_fork_in_child(cls) -> None:
        pass


##


class ForkDepthTracker(ForkHook):
    _hook_priority = -1000

    _fork_depth: ta.ClassVar[int] = 0

    @classmethod
    def _after_fork_in_child(cls) -> None:
        cls._fork_depth += 1

    @classmethod
    def get_fork_depth(cls) -> int:
        cls.install()

        return cls._fork_depth


def get_fork_depth() -> int:
    return ForkDepthTracker.get_fork_depth()


##


class ProcessOriginTracker:
    _PROCESS_COOKIE: ta.ClassVar[bytes] = os.urandom(16)

    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._process_cookie: ta.Optional[bytes] = self._PROCESS_COOKIE
        self._fork_depth: ta.Optional[int] = get_fork_depth()

    def is_in_origin_process(self) -> bool:
        return (self._PROCESS_COOKIE, get_fork_depth()) == (self._process_cookie, self._fork_depth)

    def __getstate__(self):
        return {
            **self.__dict__,
            **dict(
                _cookie=None,
                _fork_depth=None,
            ),
        }

    def __setstate__(self, state):
        self.__dict__.update(state)
