# Example of launching a subprocess and reading streaming output

from ... import curio

from . import curio_subprocess


async def main():
    p = curio_subprocess.Popen(['ping', 'www.python.org'], stdout=subprocess.PIPE)
    async for line in p.stdout:
        print('Got:', line.decode('ascii'), end='')


if __name__ == '__main__':
    curio.run(main)
