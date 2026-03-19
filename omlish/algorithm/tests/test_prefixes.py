# @omlish-lite
import unittest

from ..prefixes import build_min_unique_prefix_tree
from ..prefixes import min_unique_prefix_len
from ..prefixes import min_unique_prefix_lens


class TestMinUniquePrefixLenTrie(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(min_unique_prefix_len([]), 0)

    def test_singleton_empty(self) -> None:
        self.assertEqual(min_unique_prefix_len(['']), 0)

    def test_singleton_nonempty(self) -> None:
        self.assertEqual(min_unique_prefix_len(['abc']), 0)

    def test_simple_strings(self) -> None:
        self.assertEqual(
            min_unique_prefix_len(['abc123', 'abc456', 'abd000']),
            4,
        )

    def test_first_char_suffices(self) -> None:
        self.assertEqual(
            min_unique_prefix_len(['foo', 'bar', 'baz']),
            3,
        )

    def test_deeper_prefix_needed(self) -> None:
        self.assertEqual(
            min_unique_prefix_len(['aaaa', 'aaab', 'aaba']),
            4,
        )

    def test_mixed_lengths_but_no_prefix_collision(self) -> None:
        self.assertEqual(
            min_unique_prefix_len(['abcx', 'abcy', 'abdz']),
            4,
        )

    def test_duplicate_strings_raise(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_len(['abc', 'abc'])

    def test_prefix_of_another_raises(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_len(['ab', 'abc'])

    def test_empty_sequence_prefix_of_nonempty_raises(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_len(['', 'a'])

    def test_works_on_non_string_sequences(self) -> None:
        self.assertEqual(
            min_unique_prefix_len([
                (1, 2, 3, 4),
                (1, 2, 5, 6),
                (1, 3, 0, 0),
            ]),
            3,
        )

    def test_duplicate_non_string_sequences_raise(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_len([
                (1, 2, 3),
                (1, 2, 3),
            ])

    def test_prefix_non_string_sequences_raise(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_len([
                (1, 2),
                (1, 2, 3),
            ])

    def test_global_answer_is_max_of_per_item_needs(self) -> None:
        self.assertEqual(
            min_unique_prefix_len([
                'aaaaax',
                'aaaaay',
                'b',
            ]),
            6,
        )

    def test_bytes(self) -> None:
        self.assertEqual(
            min_unique_prefix_len([
                b'abc123',
                b'abc456',
                b'abd000',
            ]),
            4,
        )


class TestUniquePrefixLensTrie(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(min_unique_prefix_lens([]), [])

    def test_singleton_empty(self) -> None:
        self.assertEqual(min_unique_prefix_lens(['']), [0])

    def test_singleton_nonempty(self) -> None:
        self.assertEqual(min_unique_prefix_lens(['abc']), [0])

    def test_simple_strings(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens(['abc123', 'abc456', 'abd000']),
            [4, 4, 3],
        )

    def test_global_counterexample(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens(['foo', 'bar', 'baz']),
            [1, 3, 3],
        )

    def test_deeper_prefix_needed(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens(['aaaa', 'aaab', 'aaba']),
            [4, 4, 3],
        )

    def test_mixed_lengths_but_no_prefix_collision(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens(['abcx', 'abcy', 'abdz']),
            [4, 4, 3],
        )

    def test_duplicate_strings_raise(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_lens(['abc', 'abc'])

    def test_prefix_of_another_raises(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_lens(['ab', 'abc'])

    def test_empty_sequence_prefix_of_nonempty_raises(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_lens(['', 'a'])

    def test_works_on_non_string_sequences(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens([
                (1, 2, 3, 4),
                (1, 2, 5, 6),
                (1, 3, 0, 0),
            ]),
            [3, 3, 2],
        )

    def test_duplicate_non_string_sequences_raise(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_lens([
                (1, 2, 3),
                (1, 2, 3),
            ])

    def test_prefix_non_string_sequences_raise(self) -> None:
        with self.assertRaises(ValueError):
            min_unique_prefix_lens([
                (1, 2),
                (1, 2, 3),
            ])

    def test_bytes(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens([
                b'abc123',
                b'abc456',
                b'abd000',
            ]),
            [4, 4, 3],
        )

    def test_preserves_input_order(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens(['b', 'aaaaax', 'aaaaay']),
            [1, 6, 6],
        )

    def test_all_first_elements_distinct(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens(['axxx', 'bxxx', 'cxxx']),
            [1, 1, 1],
        )

    def test_two_items_diverging_at_last_element(self) -> None:
        self.assertEqual(
            min_unique_prefix_lens(['aaaaa', 'aaaab']),
            [5, 5],
        )


class TestBuildMinUniquePrefixTree(unittest.TestCase):
    def test_empty(self) -> None:
        root = build_min_unique_prefix_tree([])

        self.assertEqual(root.part, ())
        self.assertEqual(root.count, 0)
        self.assertEqual(root.terminals, set())
        self.assertEqual(root.children, {})

    def test_singleton(self) -> None:
        root = build_min_unique_prefix_tree(['abc'])

        self.assertEqual(root.part, tuple('abc'))
        self.assertEqual(root.count, 1)
        self.assertEqual(root.terminals, {tuple('abc')})
        self.assertEqual(root.children, {})

    def test_singleton_non_string_sequence(self) -> None:
        root = build_min_unique_prefix_tree([(1, 2, 3)])

        self.assertEqual(root.part, (1, 2, 3))
        self.assertEqual(root.count, 1)
        self.assertEqual(root.terminals, {(1, 2, 3)})
        self.assertEqual(root.children, {})

    def test_simple_split(self) -> None:
        root = build_min_unique_prefix_tree(['abc', 'abd'])

        self.assertEqual(root.part, ())
        self.assertEqual(root.count, 2)
        self.assertEqual(root.terminals, set())
        self.assertEqual(set(root.children.keys()), {'a'})

        a = root.children['a']
        self.assertEqual(a.part, tuple('ab'))
        self.assertEqual(a.count, 2)
        self.assertEqual(a.terminals, set())
        self.assertEqual(set(a.children.keys()), {'c', 'd'})

        c = a.children['c']
        d = a.children['d']

        self.assertEqual(c.part, tuple('c'))
        self.assertEqual(c.count, 1)
        self.assertEqual(c.terminals, {tuple('c')})
        self.assertEqual(c.children, {})

        self.assertEqual(d.part, tuple('d'))
        self.assertEqual(d.count, 1)
        self.assertEqual(d.terminals, {tuple('d')})
        self.assertEqual(d.children, {})

    def test_greedy_compression(self) -> None:
        root = build_min_unique_prefix_tree(['abc123', 'abc456', 'abd000'])

        self.assertEqual(root.part, ())
        self.assertEqual(root.count, 3)
        self.assertEqual(root.terminals, set())
        self.assertEqual(set(root.children.keys()), {'a'})

        a = root.children['a']
        self.assertEqual(a.part, tuple('ab'))
        self.assertEqual(a.count, 3)
        self.assertEqual(a.terminals, set())
        self.assertEqual(set(a.children.keys()), {'c', 'd'})

        c = a.children['c']
        d = a.children['d']

        self.assertEqual(c.part, tuple('c'))
        self.assertEqual(c.count, 2)
        self.assertEqual(c.terminals, set())
        self.assertEqual(set(c.children.keys()), {'1', '4'})

        self.assertEqual(d.part, tuple('d000'))
        self.assertEqual(d.count, 1)
        self.assertEqual(d.terminals, {tuple('d000')})
        self.assertEqual(d.children, {})

        one = c.children['1']
        four = c.children['4']

        self.assertEqual(one.part, tuple('123'))
        self.assertEqual(one.count, 1)
        self.assertEqual(one.terminals, {tuple('123')})
        self.assertEqual(one.children, {})

        self.assertEqual(four.part, tuple('456'))
        self.assertEqual(four.count, 1)
        self.assertEqual(four.terminals, {tuple('456')})
        self.assertEqual(four.children, {})

    def test_non_string_sequences(self) -> None:
        root = build_min_unique_prefix_tree([
            (1, 2, 3, 4),
            (1, 2, 5, 6),
            (1, 3, 0, 0),
        ])

        self.assertEqual(root.part, ())
        self.assertEqual(root.count, 3)
        self.assertEqual(root.terminals, set())
        self.assertEqual(set(root.children.keys()), {1})

        one = root.children[1]
        self.assertEqual(one.part, (1,))
        self.assertEqual(one.count, 3)
        self.assertEqual(one.terminals, set())
        self.assertEqual(set(one.children.keys()), {2, 3})

        two = one.children[2]
        three = one.children[3]

        self.assertEqual(two.part, (2,))
        self.assertEqual(two.count, 2)
        self.assertEqual(two.terminals, set())
        self.assertEqual(set(two.children.keys()), {3, 5})

        self.assertEqual(three.part, (3, 0, 0))
        self.assertEqual(three.count, 1)
        self.assertEqual(three.terminals, {(3, 0, 0)})
        self.assertEqual(three.children, {})

    def test_duplicate_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_min_unique_prefix_tree(['abc', 'abc'])

    def test_prefix_of_another_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_min_unique_prefix_tree(['ab', 'abc'])

    def test_empty_sequence_prefix_of_nonempty_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_min_unique_prefix_tree(['', 'a'])

    def test_duplicate_empty_sequences_raise(self) -> None:
        with self.assertRaises(ValueError):
            build_min_unique_prefix_tree(['', ''])
