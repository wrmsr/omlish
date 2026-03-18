# @omlish-lite
import unittest

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
