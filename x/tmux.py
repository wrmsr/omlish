"""
https://github.com/tmux-python/libtmux

https://github.com/tmux-python/tmuxp
"""
import libtmux as tx


def _main() -> None:
    server = tx.Server()
    server.cmd('display-message', 'hello world')


if __name__ == '__main__':
    _main()
