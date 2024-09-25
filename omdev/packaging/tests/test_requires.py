# ruff: noqa: PT009
import unittest

from ..requires import parse_requirement


class TestSpecifiers(unittest.TestCase):
    def test_requires(self):
        for s in [
            """pytest-mypy ; (platform_python_implementation != "PyPy") and extra == 'testing'""",
        ]:
            parse_requirement(s)
