import yaml

from .... import lang
from .... import marshal as msh
from ....formats import json
from ..openapi import Openapi


def test_openapi():
    yml_src = lang.get_relative_resources('.', globals=globals())['example.yml'].read_bytes().decode('utf-8')
    doc = yaml.safe_load(yml_src)

    api = msh.unmarshal(doc, Openapi)

    print(json.dumps_pretty(msh.marshal(api)))
