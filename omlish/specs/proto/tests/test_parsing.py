from .... import lang
from ..parsing import parse_proto


def test_parse_proto():
    src = lang.get_relative_resources('.examples', globals=globals())['addressbook.proto'].read_text()
    print(parse_proto(src))
