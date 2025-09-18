import json  # noqa

from ...... import lang
from ...utils import stream_parse_exactly_one_value  # noqa


def _main() -> None:
    # loads = json.loads
    loads = stream_parse_exactly_one_value

    long_string_json = '{"a_long_string": "%s"}' % ('0123456789abcdef' * (64 * 1024),)  # noqa

    p = 40
    with lang.Timer() as tmr:
        obj = loads([long_string_json[:p], long_string_json[p:]])

    print(f'{tmr.elapsed * 1_000.:_} ms')

    assert obj == json.loads(long_string_json)


if __name__ == '__main__':
    _main()
