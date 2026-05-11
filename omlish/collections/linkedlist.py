# ruff: noqa: SLF001
import abc
import operator
import typing as ta

from .. import lang


N = ta.TypeVar('N')
T = ta.TypeVar('T')
T2 = ta.TypeVar('T2')

NodeLinkedListNodeT = ta.TypeVar('NodeLinkedListNodeT', bound='NodeLinkedList._Node')


##


class BaseLinkedList(lang.Abstract, ta.Generic[N]):
    _head_node: N | None = None
    _tail_node: N | None = None

    #

    @abc.abstractmethod
    def _get_node_prev(self, node: N) -> N | None:
        raise NotImplementedError

    @abc.abstractmethod
    def _set_node_prev(self, node: N, prev_node: N | None) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_node_next(self, node: N) -> N | None:
        raise NotImplementedError

    @abc.abstractmethod
    def _set_node_next(self, node: N, next_node: N | None) -> None:
        raise NotImplementedError

    #

    def _insert_node_between(
            self,
            prev_node: N | None,
            node: N,
            next_node: N | None,
    ) -> None:
        if prev_node is not None:
            self._set_node_next(prev_node, node)
        else:
            self._head_node = node

        if next_node is not None:
            self._set_node_prev(next_node, node)
        else:
            self._tail_node = node

        self._set_node_prev(node, prev_node)
        self._set_node_next(node, next_node)

    def _prepend_node(self, node: N) -> None:
        self._insert_node_between(None, node, self._head_node)

    def _insert_node_before(self, target: N, node: N) -> None:
        self._insert_node_between(self._get_node_prev(target), node, target)

    def _insert_node_after(self, target: N, node: N) -> None:
        self._insert_node_between(target, node, self._get_node_next(target))

    def _append_node(self, node: N) -> None:
        self._insert_node_between(self._tail_node, node, None)

    #

    def _unlink_node(self, node: N) -> None:
        prev_node = self._get_node_prev(node)
        next_node = self._get_node_next(node)

        if prev_node is not None:
            self._set_node_next(prev_node, next_node)
        else:
            self._head_node = next_node

        if next_node is not None:
            self._set_node_prev(next_node, prev_node)
        else:
            self._tail_node = prev_node

        self._set_node_prev(node, None)
        self._set_node_next(node, None)


##


class NodeLinkedList(BaseLinkedList[NodeLinkedListNodeT], lang.Abstract, ta.Generic[T, NodeLinkedListNodeT]):
    class _Node(ta.Protocol):
        @property
        def _node_prev(self) -> ta.Self | None: ...

        @_node_prev.setter
        def _node_prev(self, node_prev: ta.Self | None) -> None: ...

        @property
        def _node_next(self) -> ta.Self | None: ...

        @_node_next.setter
        def _node_next(self, node_next: ta.Self | None) -> None: ...

    #

    _get_node_prev = staticmethod(operator.attrgetter('_node_prev'))  # type: ignore[assignment]
    _set_node_prev = staticmethod(lang.attrsetter('_node_prev'))  # type: ignore[assignment]
    _get_node_next = staticmethod(operator.attrgetter('_node_next'))  # type: ignore[assignment]
    _set_node_next = staticmethod(lang.attrsetter('_node_next'))  # type: ignore[assignment]


##


class OpenLinkedList(NodeLinkedList[T, 'OpenLinkedList.Node[T]'], ta.Generic[T]):
    class Node(ta.Generic[T2]):
        def __init__(self, value: T2) -> None:
            self.value = value

        _node_prev: OpenLinkedList.Node[T2] | None = None
        _node_next: OpenLinkedList.Node[T2] | None = None

        @property
        def node_prev(self) -> OpenLinkedList.Node[T2] | None:
            return self._node_prev

        @property
        def node_next(self) -> OpenLinkedList.Node[T2] | None:
            return self._node_next

    def new_node(self, value: T) -> Node[T]:
        return self.Node(value)

    #

    @property
    def head_node(self) -> Node[T] | None:
        return self._head_node

    @property
    def tail_node(self) -> Node[T] | None:
        return self._tail_node

    #

    insert_node_between = NodeLinkedList._insert_node_between
    prepend_node = NodeLinkedList._prepend_node
    insert_node_before = NodeLinkedList._insert_node_before
    insert_node_after = NodeLinkedList._insert_node_after
    append_node = NodeLinkedList._append_node

    unlink_node = NodeLinkedList._unlink_node

    #

    def insert_between(
            self,
            prev_node: Node[T] | None,
            value: T,
            next_node: Node[T] | None,
    ) -> Node[T]:
        self._insert_node_between(
            prev_node,
            node := self.Node(value),
            next_node,
        )
        return node

    def prepend(self, value: T) -> Node[T]:
        self._prepend_node(node := self.Node(value))
        return node

    def insert_before(self, target: Node[T], value: T) -> Node[T]:
        self._insert_node_before(target, node := self.Node(value))
        return node

    def insert_after(self, target: Node[T], value: T) -> Node[T]:
        self._insert_node_after(target, node := self.Node(value))
        return node

    def append(self, value: T) -> Node[T]:
        self._append_node(node := self.Node(value))
        return node
