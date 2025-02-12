# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - ForkHook base class? all classmethods? prevents pickling
"""
import abc
import os
import threading
import typing as ta

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

    class Hook(ta.NamedTuple):
        key: ta.Any
        priority: int

        # NOTE: these are called inside the global, non-reentrant manager lock
        before_fork: ta.Optional[ta.Callable[[], None]] = None
        after_fork_in_parent: ta.Optional[ta.Callable[[], None]] = None
        after_fork_in_child: ta.Optional[ta.Callable[[], None]] = None

    _hooks_by_key: ta.ClassVar[ta.Dict[int, Hook]] = {}

    class HookAlreadyPresentError(Exception):
        pass

    @classmethod
    def add_hook(cls, hook: Hook) -> None:
        with cls._lock:
            if hook.key in cls._hooks_by_key:
                raise cls.HookAlreadyPresentError(hook.key)

            check.isinstance(hook.priority, int)

            cls._hooks_by_key[hook.key] = hook
            cls._rebuild_priority_list()

            cls._install()

    @classmethod
    def try_add_hook(cls, hook: Hook) -> bool:
        try:
            cls.add_hook(hook)
        except cls.HookAlreadyPresentError:
            return False
        else:
            return True

    @classmethod
    def contains_hook(cls, key: ta.Any) -> bool:
        with cls._lock:
            return key in cls._hooks_by_key

    @classmethod
    def remove_hook(cls, key: ta.Any) -> None:
        with cls._lock:
            del cls._hooks_by_key[key]

            cls._rebuild_priority_list()

    #

    _priority_ordered_hooks: ta.ClassVar[ta.List[Hook]] = []

    @classmethod
    def _rebuild_priority_list(cls) -> None:
        # Uses on dict order preservation for insertion-order of hooks of equal priority (although that shouldn't be
        # depended upon for usecase correctness.
        cls._priority_ordered_hooks = sorted(cls._hooks_by_key.values(), key=lambda h: h.priority)

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


class ForkHook(abc.ABC):  # noqa
    @ta.final
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @classmethod
    @ta.final
    def _install(cls) -> bool:
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
            cls._install()

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


class _ForkDepthTracker(ForkHook):
    _fork_depth: ta.ClassVar[int] = 0

    @classmethod
    def _after_fork_in_child(cls) -> None:
        cls._fork_depth += 1

    @classmethod
    def get_fork_depth(cls) -> int:
        cls._install()

        return cls._fork_depth


def get_fork_depth() -> int:
    return _ForkDepthTracker.get_fork_depth()
