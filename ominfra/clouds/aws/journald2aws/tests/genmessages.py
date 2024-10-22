import argparse
import datetime
import json
import time
import uuid


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int, default=10, nargs='?')
    parser.add_argument('--sleep-s', type=float, nargs='?')
    parser.add_argument('--sleep-n', type=int, nargs='?')
    args = parser.parse_args()

    for i in range(args.n):
        if args.sleep_s:
            if not args.sleep_n or (i and i % args.sleep_n == 0):
                time.sleep(args.sleep_s)

        dct = {
            'MESSAGE': f'message {i}',
            'MESSAGE_ID': uuid.uuid4().hex,
            '__CURSOR': f'cursor:{i}',
            '_SOURCE_REALTIME_TIMESTAMP': str(int(datetime.datetime.now(tz=datetime.UTC).timestamp() * 1_000_000)),
        }
        print(json.dumps(dct, indent=None, separators=(',', ':')))


if __name__ == '__main__':
    _main()
