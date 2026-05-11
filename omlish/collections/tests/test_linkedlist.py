from ..linkedlist import OpenLinkedList


def vals_forward(ll: OpenLinkedList[int]) -> list[int]:
    out: list[int] = []
    cur = ll.head_node
    while cur is not None:
        out.append(cur.value)
        cur = cur.node_next
    return out


def vals_reverse(ll: OpenLinkedList[int]) -> list[int]:
    out: list[int] = []
    cur = ll.tail_node
    while cur is not None:
        out.append(cur.value)
        cur = cur.node_prev
    return out


def assert_links(ll: OpenLinkedList[int], nodes: list[OpenLinkedList.Node[int]]) -> None:
    assert vals_forward(ll) == [n.value for n in nodes]
    assert vals_reverse(ll) == [n.value for n in reversed(nodes)]

    assert ll.head_node is (nodes[0] if nodes else None)
    assert ll.tail_node is (nodes[-1] if nodes else None)

    for i, n in enumerate(nodes):
        assert n.node_prev is (nodes[i - 1] if i else None)
        assert n.node_next is (nodes[i + 1] if i + 1 < len(nodes) else None)


def ns(*values: int) -> list[OpenLinkedList.Node[int]]:
    return [OpenLinkedList.Node(v) for v in values]


def test_open_linked_list_initially_empty() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()

    assert ll.head_node is None
    assert ll.tail_node is None
    assert vals_forward(ll) == []
    assert vals_reverse(ll) == []


def test_open_linked_list_append_single_node() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, = ns(1)

    ll.append_node(a)

    assert_links(ll, [a])


def test_open_linked_list_append_multiple_nodes() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(b)
    ll.append_node(c)

    assert_links(ll, [a, b, c])


def test_open_linked_list_prepend_single_node() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, = ns(1)

    ll.prepend_node(a)

    assert_links(ll, [a])


def test_open_linked_list_prepend_multiple_nodes() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.prepend_node(c)
    ll.prepend_node(b)
    ll.prepend_node(a)

    assert_links(ll, [a, b, c])


def test_open_linked_list_mixed_append_prepend() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c, d = ns(1, 2, 3, 4)

    ll.append_node(b)
    ll.prepend_node(a)
    ll.append_node(c)
    ll.prepend_node(d)

    assert_links(ll, [d, a, b, c])


def test_open_linked_list_insert_before_head() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b = ns(1, 2)

    ll.append_node(b)
    ll.insert_node_before(b, a)

    assert_links(ll, [a, b])


def test_open_linked_list_insert_before_middle() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c, d = ns(1, 2, 3, 4)

    ll.append_node(a)
    ll.append_node(c)
    ll.append_node(d)
    ll.insert_node_before(c, b)

    assert_links(ll, [a, b, c, d])


def test_open_linked_list_insert_before_tail() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(c)
    ll.insert_node_before(c, b)

    assert_links(ll, [a, b, c])


def test_open_linked_list_insert_after_head() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(c)
    ll.insert_node_after(a, b)

    assert_links(ll, [a, b, c])


def test_open_linked_list_insert_after_middle() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c, d = ns(1, 2, 3, 4)

    ll.append_node(a)
    ll.append_node(b)
    ll.append_node(d)
    ll.insert_node_after(b, c)

    assert_links(ll, [a, b, c, d])


def test_open_linked_list_insert_after_tail() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b = ns(1, 2)

    ll.append_node(a)
    ll.insert_node_after(a, b)

    assert_links(ll, [a, b])


def test_open_linked_list_insert_between_empty() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, = ns(1)

    ll.insert_node_between(None, a, None)

    assert_links(ll, [a])


def test_open_linked_list_insert_between_head_and_tail() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(c)
    ll.insert_node_between(a, b, c)

    assert_links(ll, [a, b, c])


def test_open_linked_list_unlink_only_node() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, = ns(1)

    ll.append_node(a)
    ll.unlink_node(a)

    assert_links(ll, [])
    assert a.node_prev is None
    assert a.node_next is None


def test_open_linked_list_unlink_head() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(b)
    ll.append_node(c)
    ll.unlink_node(a)

    assert_links(ll, [b, c])
    assert a.node_prev is None
    assert a.node_next is None


def test_open_linked_list_unlink_middle() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(b)
    ll.append_node(c)
    ll.unlink_node(b)

    assert_links(ll, [a, c])
    assert b.node_prev is None
    assert b.node_next is None


def test_open_linked_list_unlink_tail() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(b)
    ll.append_node(c)
    ll.unlink_node(c)

    assert_links(ll, [a, b])
    assert c.node_prev is None
    assert c.node_next is None


def test_open_linked_list_unlink_all_from_head_to_tail() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(b)
    ll.append_node(c)

    ll.unlink_node(a)
    assert_links(ll, [b, c])

    ll.unlink_node(b)
    assert_links(ll, [c])

    ll.unlink_node(c)
    assert_links(ll, [])

    assert a.node_prev is a.node_next is None
    assert b.node_prev is b.node_next is None
    assert c.node_prev is c.node_next is None


def test_open_linked_list_unlink_all_from_tail_to_head() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(b)
    ll.append_node(c)

    ll.unlink_node(c)
    assert_links(ll, [a, b])

    ll.unlink_node(b)
    assert_links(ll, [a])

    ll.unlink_node(a)
    assert_links(ll, [])

    assert a.node_prev is a.node_next is None
    assert b.node_prev is b.node_next is None
    assert c.node_prev is c.node_next is None


def test_open_linked_list_unlinked_node_can_be_reinserted() -> None:
    ll: OpenLinkedList[int] = OpenLinkedList()
    a, b, c = ns(1, 2, 3)

    ll.append_node(a)
    ll.append_node(b)
    ll.unlink_node(a)
    ll.append_node(c)
    ll.append_node(a)

    assert_links(ll, [b, c, a])


def test_open_linked_list_multiple_instances_are_independent() -> None:
    ll1: OpenLinkedList[int] = OpenLinkedList()
    ll2: OpenLinkedList[int] = OpenLinkedList()
    a, b = ns(1, 2)

    ll1.append_node(a)
    ll2.append_node(b)

    assert_links(ll1, [a])
    assert_links(ll2, [b])
