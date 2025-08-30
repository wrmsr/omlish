import time


n = 10_000_000
d = {0: 0}

s = time.monotonic()

for _ in range(n):
    d[0]  # noqa

e = time.monotonic()

print(f'{(e - s) / n * 1_000_000_000} ns')
