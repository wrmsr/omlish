import os.path
import unittest

from ..supervisor import main


class TestSupervisor(unittest.TestCase):
    def test_supervisor(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'demo.json')
        main(
            [conf_file],
            test=True,
            # no_logging=True,
        )
