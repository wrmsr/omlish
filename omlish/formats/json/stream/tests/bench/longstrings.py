import json  # noqa

from ...... import lang
from ...utils import stream_parse_exactly_one_value  # noqa


def _main() -> None:
    # loads = json.loads
    loads = stream_parse_exactly_one_value

    long_string_json = '{"a_long_string": "%s"}' % ('0123456789abcdef' * (64 * 1024),)  # noqa

    with lang.Timer() as tmr:
        loads(long_string_json)

    print(f'{tmr.elapsed * 1_000.:_} ms')


if __name__ == '__main__':
    _main()
