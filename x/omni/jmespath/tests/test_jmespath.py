import copy
import json
import os.path

import pytest

from .. import eval as eval_
from .. import parsing as parsing_


def test_jmespath():
    node = parsing_.parse("locations[?state == 'WA'].name | sort(@) | {WashingtonCities: join(', ', @)}")
    print(node)


@pytest.mark.xfail()
def test_cases():
    path = os.path.join(os.path.dirname(__file__), 'json')
    for name in os.listdir(path):
        if not name.endswith('.json') or name == 'schema.json':
            continue
        with open(os.path.join(path, name), 'r') as f:
            buf = f.read()
        suites = json.loads(buf)

        for suite in suites:
            for case in suite['cases']:
                try:
                    node = parsing_.parse(case['expression'])
                except Exception as e:  # noqa
                    assert case.get('error') == 'syntax'
                    continue

                print(node)

                runtime = eval_.RuntimeImpl()
                evaluator = eval_.Evaluator(runtime)

                given = copy.deepcopy(suite['given'])
                result = evaluator(node, given)

                print(result)
