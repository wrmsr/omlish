import os.path


def _main() -> None:
    root_dir = os.path.expanduser('~/src/paul-gauthier/2048')
    os.chdir(root_dir)

    with open(os.path.expanduser('~/.omlish-llm/.env')) as f:
        os.environ.update({
            k: v
            for l in f
            if (s := l.strip())
            for k, v in [s.split('=')]
        })

    from .initial.coder import Coder

    coder = Coder(True, ['js/game_manager.js'], False)

    coder._handle_input('What is this repo?')  # noqa


if __name__ == '__main__':
    _main()
