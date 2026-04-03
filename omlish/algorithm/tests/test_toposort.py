import unittest

from ..toposort import mut_toposort
from ..toposort import toposort


def _layers(it):
    return [frozenset(s) for s in it]


class ToposortTests(unittest.TestCase):
    def test_direction_is_item_to_dependencies(self):
        data = {
            'review': {'business', 'user'},
            'business': set(),
            'user': set(),
        }

        self.assertEqual(
            _layers(toposort(data)),
            [frozenset({'business', 'user'}), frozenset({'review'})],
        )

    def test_dependency_only_items_are_added_implicitly(self):
        data = {
            'review': {'business', 'user'},
        }

        self.assertEqual(
            _layers(toposort(data)),
            [frozenset({'business', 'user'}), frozenset({'review'})],
        )

    def test_multiple_layers(self):
        data = {
            'deploy': {'build'},
            'build': {'test'},
            'test': {'lint'},
            'lint': set(),
        }

        self.assertEqual(
            _layers(toposort(data)),
            [
                frozenset({'lint'}),
                frozenset({'test'}),
                frozenset({'build'}),
                frozenset({'deploy'}),
            ],
        )

    def test_independent_items_share_a_layer(self):
        data = {
            'a': set(),
            'b': set(),
            'c': {'a'},
        }

        self.assertEqual(
            _layers(toposort(data)),
            [frozenset({'a', 'b'}), frozenset({'c'})],
        )

    def test_self_dependency_is_ignored(self):
        data = {
            'a': {'a'},
        }

        self.assertEqual(
            _layers(toposort(data)),
            [frozenset({'a'})],
        )

    def test_cycle_raises(self):
        data = {
            'a': {'b'},
            'b': {'a'},
        }

        with self.assertRaises(ValueError) as cm:
            list(toposort(data))

        self.assertIn('Cyclic dependencies exist', str(cm.exception))

    def test_cycle_after_acyclic_prefix_raises(self):
        data = {
            'a': set(),
            'b': {'c'},
            'c': {'b'},
        }

        it = toposort(data)
        self.assertEqual(next(it), {'a'})
        with self.assertRaises(ValueError):
            list(it)

    def test_toposort_does_not_mutate_input(self):
        data = {
            'a': {'a', 'b'},
            'b': set(),
        }
        original = {k: set(v) for k, v in data.items()}

        list(toposort(data))

        self.assertEqual(data, original)

    def test_mut_toposort_mutates_input_up_front(self):
        data = {
            'a': {'a', 'b'},
        }

        list(mut_toposort(data))

        # self-dependency discarded
        self.assertEqual(data['a'], {'b'})
        # dependency-only item added
        self.assertIn('b', data)
        self.assertEqual(data['b'], set())

    def test_empty_input(self):
        self.assertEqual(_layers(toposort({})), [])
