#!/usr/bin/env python
"""
Main function: get_struct
Usage:
echo '{"some_json": "string"}' | describe_json.py

MIT License

Copyright (c) 2019 Vlad George Ardelean

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import print_function, unicode_literals
import json
import sys
import argparse
import string
import random
from hashlib import md5


ALLOWED_CHARS = set(string.ascii_letters) | set(string.digits)

MAX_STRING_DEFAULT = 10
MAX_ARRAY_DEFAULT = 1
RANDOMIZE_DEFAULT = False
JQ_FULLPATH_KEYS_DEFAULT = False


def is_basestring(obj):
    """Provides py2/3 compat"""
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)


class JSONDescriber(object):
    def __init__(
            self,
            max_array_size=MAX_ARRAY_DEFAULT,
            max_string_size=MAX_STRING_DEFAULT,
            randomize=RANDOMIZE_DEFAULT,
            jq_fullpath_keys=JQ_FULLPATH_KEYS_DEFAULT,
    ):
        self.max_array_size = max_array_size
        self.max_string_size = max_string_size
        self.randomize = randomize
        self.jq_fullpath_keys = jq_fullpath_keys

    def get_struct(self, obj, path_elems=''):
        """Entrypoint. Use this function with any object that was json.load-ed

        >>> JSONDescriber().get_struct(0)
        0

        >>> JSONDescriber().get_struct([1, 2, 3])
        ['length: 3; example:', 1]

        >>> JSONDescriber().get_struct({'a': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'})
        {'a': 'aaaaaaaaaa... len: 44, md5: 4c3c7c067634daec9716a80ea886d123'}

        >>> JSONDescriber().get_struct({'a':['aaaaaaaaaaaa0000000000000000']})
        {'a': ['aaaaaaaaaa... len: 28, md5: 27612b87a33aa5280b0cd000b3e75e4d']}

        The "== {}" syntax is because dict keys are not necessarily ordered.
        This makes the test pass on all 2.7+/3+ versions of python
        >>> JSONDescriber().get_struct({'a': 'b', 'c': 'd'}) == \
        {'a': 'b', 'c': 'd'}
        True

        The "== {}" syntax is because dict keys are not necessarily ordered.
        This makes the test pass on all 2.7+/3+ versions of python
        >>> JSONDescriber().get_struct({'c': 'd', 'e': [1, 2, 3]}) == \
        {'c': 'd', 'e': ['length: 3; example:', 1]}
        True

        The "== {}" syntax is because dict keys are not necessarily ordered.
        This makes the test pass on all 2.7+/3+ versions of python
        >>> JSONDescriber().get_struct({'e': [{'e': 'f', 'g': 'g', 'h': 'aaaaaaaaaaaa'}]}) == \
        {'e': [{'e': 'f', 'g': 'g', 'h': 'aaaaaaaaaa... len: 12, md5: 45e4812014d83dde5666ebdf5a8ed1ed'}]}
        True

        >>> JSONDescriber(jq_fullpath_keys=True).get_struct({"a": {"b": [{"c": 1}]}})
        {'.a': {'.a.b': [{'.a.b[0].c': 1}]}}

        :param obj:
        :return:
        """
        if not isinstance(obj, (dict, list, tuple, set)):
            return self.get_scalar_struct(obj)
        elif isinstance(obj, (list, tuple, set)):
            return self.get_array_struct(obj, path_elems)
        elif isinstance(obj, dict):
            return self.get_object_struct(obj, path_elems)

    def get_scalar_struct(self, value):
        if is_basestring(value) and len(value) > self.max_string_size:
            return "{}... len: {}, md5: {}".format(
                value[:self.max_string_size],
                len(value),
                md5(value.encode('utf-8')).hexdigest()
            )
        return value

    def get_array_struct(self, array, path_elems=''):
        if len(array) > self.max_array_size:
            if self.randomize:
                index = random.randint(0, len(array) - 1)
            else:
                index = 0

            return [
                'length: {}; example:'.format(len(array)),
                self.get_struct(
                    array[index], "{}[{}]".format(path_elems, index),
                )
            ]
        else:
            return [self.get_struct(elem, "{}[{}]".format(path_elems, idx)) for idx,elem in enumerate(array)]

    def get_object_struct(self, dict_obj, path_elems=''):
        """Transforms data deep data structures recursively, replacing lists/tuples
        with a dict describing how many elements the collection had, and outputting
        the first elem, as an example

        :param dict dict_obj:
        :return:
        """
        result = {}
        for key, value in dict_obj.items():
            usable_key = key if not self.jq_fullpath_keys else "{}.{}".format(path_elems, self._quote_key(key))
            result[usable_key] = self.get_struct(value, usable_key)

        return result

    def _quote_key(self, key):
        if set(key) - ALLOWED_CHARS:
            # 1. escape quotes
            # 2. quote
            return '"{}"'.format(key.replace('"', '\"'))
        else:
            return key


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file',
        help="The path to a file to use instead of reading 1-line JSON strings"
             " from stdin",
        default=None,
        type=str,
    )
    parser.add_argument(
        '-a', '--max-array-size',
        help="The maximum array size that we can allow to be outputted. "
             "If the array is longer, it will be displayed as containing 2 "
             "elements: a string which displays its size, and just one of "
             "the original elements in the array",
        default=MAX_ARRAY_DEFAULT,
        type=int,
        dest='max_array_size',
    )
    parser.add_argument(
        '-s', '--max-string-size',
        help="The maximum string length that we can allow to be outputted. "
             "If the string is longer, it will be displayed shortened.",
        default=MAX_STRING_DEFAULT,
        type=int,
        dest='max_string_size',
    )
    parser.add_argument(
        '-j', '--jq-fullpath-keys',
        help='Converts keys to full jq path specs. Useful when wanting to '
            'print afterwards just a specific key',
        action='store_true',
        dest='jq_fullpath_keys',
    )
    parser.add_argument(
        '-r', '--randomize-array-member',
        help='By default, the library will display only the first member of '
             'arrays as an example. Setting this flag, will make it so a '
             'random array member is chosen',
        action='store_true',
        dest='randomize',
    )
    parser.add_argument(
        'json_string',
        help='A JSON string to parse. You can either provide this, or pipe '
             'the JSON through.',
        nargs='?'
    )

    args = parser.parse_args()

    json_describer = JSONDescriber(
        max_array_size=args.max_array_size,
        max_string_size=args.max_string_size,
        randomize=args.randomize,
        jq_fullpath_keys=args.jq_fullpath_keys,
    )

    if not args.file:
        if sys.stdin.isatty() and not args.json_string:
            parser.print_help()
        elif args.json_string:
            print(json.dumps(
                json_describer.get_struct(json.loads(args.json_string))))

        else:
            # Do not assume that 1 line = 1 JSON obj.
            # Instead, allow each JSON to span one or multiple lines
            lines = []
            num_open_braces = 0
            num_closed_braces = 0
            for line in sys.stdin:
                num_open_braces += line.count('{')
                num_closed_braces += line.count('}')
                lines.append(line)

                # this is a performance optimization.
                # it costs us relatively little to do a char count
                # but parsing/unparsing huge JSON files, line by line is
                # extremely costly, comparatively
                if num_open_braces == num_closed_braces:
                    try:
                        print(
                            json.dumps(
                                json_describer.get_struct(
                                    json.loads('\n'.join(lines))))
                        )

                        lines = []
                        num_open_braces = 0
                        num_closed_braces = 0

                    except ValueError as err:
                        pass

    else:
        with open(args.file) as json_file:
            print(json.dumps(
                json_describer.get_struct(json.load(json_file))))


if __name__ == '__main__':
    main()