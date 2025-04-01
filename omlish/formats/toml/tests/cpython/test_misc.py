# ruff: noqa: PT009 PT027
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Taneli Hukkinen
# Licensed to PSF under a Contributor Agreement.
import copy
import datetime
import decimal
import pathlib
import sys
import tempfile
import unittest

from ... import parser
from . import support


class TestMiscellaneous(unittest.TestCase):
    def test_load(self):
        content = "one=1 \n two='two' \n arr=[]"
        expected = {'one': 1, 'two': 'two', 'arr': []}
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            file_path = pathlib.Path(tmp_dir_path) / 'test.toml'
            file_path.write_text(content)

            with open(file_path, 'rb') as bin_f:
                actual = parser.toml_load(bin_f)
        self.assertEqual(actual, expected)

    def test_incorrect_load(self):
        content = 'one=1'
        with tempfile.TemporaryDirectory() as tmp_dir_path:
            file_path = pathlib.Path(tmp_dir_path) / 'test.toml'
            file_path.write_text(content)

            with open(file_path) as txt_f:
                with self.assertRaises(TypeError):
                    parser.toml_load(txt_f)  # type: ignore[arg-type]

    def test_parse_float(self):
        doc = """
              val=0.1
              biggest1=inf
              biggest2=+inf
              smallest=-inf
              notnum1=nan
              notnum2=-nan
              notnum3=+nan
              """
        obj = parser.toml_loads(doc, parse_float=decimal.Decimal)
        expected = {
            'val': decimal.Decimal('0.1'),
            'biggest1': decimal.Decimal('inf'),
            'biggest2': decimal.Decimal('inf'),
            'smallest': decimal.Decimal('-inf'),
            'notnum1': decimal.Decimal('nan'),
            'notnum2': decimal.Decimal('-nan'),
            'notnum3': decimal.Decimal('nan'),
        }
        for k, expected_val in expected.items():
            actual_val = obj[k]
            self.assertIsInstance(actual_val, decimal.Decimal)
            if actual_val.is_nan():
                self.assertTrue(expected_val.is_nan())
            else:
                self.assertEqual(actual_val, expected_val)

    def test_deepcopy(self):
        doc = """
              [bliibaa.diibaa]
              offsettime=[1979-05-27T00:32:00.999999-07:00]
              """
        obj = parser.toml_loads(doc)
        obj_copy = copy.deepcopy(obj)
        self.assertEqual(obj_copy, obj)
        expected_obj = {
            'bliibaa': {
                'diibaa': {
                    'offsettime': [
                        datetime.datetime(
                            1979,
                            5,
                            27,
                            0,
                            32,
                            0,
                            999999,
                            tzinfo=datetime.timezone(datetime.timedelta(hours=-7)),
                        ),
                    ],
                },
            },
        }
        self.assertEqual(obj_copy, expected_obj)

    def test_inline_array_recursion_limit(self):
        with support.infinite_recursion(max_depth=100):
            available = support.get_recursion_available()
            nest_count = (available // 2) - 2
            # Add details if the test fails
            with self.subTest(
                    limit=sys.getrecursionlimit(),
                    available=available,
                    nest_count=nest_count,
            ):
                recursive_array_toml = 'arr = ' + nest_count * '[' + nest_count * ']'
                parser.toml_loads(recursive_array_toml)

    def test_inline_table_recursion_limit(self):
        with support.infinite_recursion(max_depth=100):
            available = support.get_recursion_available()
            nest_count = (available // 3) - 1
            # Add details if the test fails
            with self.subTest(
                    limit=sys.getrecursionlimit(),
                    available=available,
                    nest_count=nest_count,
            ):
                recursive_table_toml = nest_count * 'key = {' + nest_count * '}'
                parser.toml_loads(recursive_table_toml)
