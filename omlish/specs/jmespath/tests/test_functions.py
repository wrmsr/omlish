# ruff: noqa: PT009 PT027
import datetime
import json
import unittest

from ... import jmespath


class TestFunctions(unittest.TestCase):
    def test_can_max_datetimes(self):
        # This is python specific behavior, but Jmespath does not specify what you should do with language specific
        # types.  We're going to add the ability that ``to_string`` will always default to str()'ing values it doesn't
        # understand.
        data = [datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(seconds=1)]  # noqa
        result = jmespath.search('max([*].to_string(@))', data)
        self.assertEqual(json.loads(result), str(data[-1]))

    def test_type_error_messages(self):
        with self.assertRaises(jmespath.errors.JmespathTypeError) as e:
            jmespath.search('length(@)', 2)
        exception = e.exception
        # 1. Function name should be in error message
        self.assertIn('length()', str(exception))
        # 2. Mention it's an invalid type
        self.assertIn('invalid type for value: 2', str(exception))
        # 3. Mention the valid types:
        self.assertIn("expected one of: ['string', 'array', 'object']", str(exception))
        # 4. Mention the actual type.
        self.assertIn('received: "number"', str(exception))

    def test_singular_in_error_message(self):
        with self.assertRaises(jmespath.errors.ArityError) as e:
            jmespath.search('length(@, @)', [0, 1])
        exception = e.exception
        self.assertEqual(
            str(exception), 'Expected 1 argument for function length(), received 2',
        )

    def test_error_message_is_pluralized(self):
        with self.assertRaises(jmespath.errors.ArityError) as e:
            jmespath.search('sort_by(@)', [0, 1])
        exception = e.exception
        self.assertEqual(
            str(exception), 'Expected 2 arguments for function sort_by(), received 1',
        )

    def test_variadic_is_pluralized(self):
        with self.assertRaises(jmespath.errors.VariadicArityError) as e:
            jmespath.search('not_null()', 'foo')
        exception = e.exception
        self.assertEqual(
            str(exception),
            'Expected at least 1 argument for function not_null(), received 0',
        )
