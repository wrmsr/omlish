import itertools
import json
import re
import sys


"""
parts = [
    '54.244.199.9',
    '-',
    '-',
    '[20/Jul/2024:17:54:01 +0000]',
    '"GET /profile/jenkinsFile HTTP/1.1"',
    '404',
    '555',
    '"-"',
    '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"',
]

==

remote_addr
-
remote_user
[time_local]
"request"
status
body_bytes_sent
"http_referer"
"http_user_agent"

==

remote_addr
-
remote_user
time_local
request
status
body_bytes_sent
http_referer
http_user_agent

"""


def _main() -> None:
    pat = re.compile(r'("[^"]*")|(\[^\]*\]")|([^ ]+)')
    for s in sys.stdin:
        l = list(itertools.batched(pat.split(s), 3))
        v = [a or b for t in l if len(t) > 1 for _, a, b in [t]]
        
        
if __name__ == '__main__':
    _main()
