import unittest
import tempfile

from ..interps import VenvInterps


_TEST_VERSIONS_FILE = """
PYTHON_8=3.8.19
PYTHON_9=3.9.19
PYTHON_10=3.10.14
PYTHON_11=3.11.9
PYTHON_12=3.12.5
PYTHON_13=3.13.0rc1
PYTHON_13T=3.13.0rc1t
PYTHON_DEV=3.14-dev
"""


class TestInterps(unittest.TestCase):
    def test_venv_interps(self):
        with open((vf := tempfile.mktemp('-omdev-pyproject2')), 'w') as f:
            f.write(_TEST_VERSIONS_FILE)
        print(VenvInterps(versions_file=vf).versions_file_pythons())
