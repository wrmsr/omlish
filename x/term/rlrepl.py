import atexit
import os
import pathlib
import shlex
import typing as ta


try:
    import readline  # noqa
except ImportError:
    HAVE_READLINE = False
else:
    HAVE_READLINE = True


##


def cmd_say(args: ta.Sequence[str]) -> None:
    print(' '.join(args))


def cmd_shout(args: ta.Sequence[str]) -> None:
    print(' '.join(args).upper())


def cmd_help(_: ta.Sequence[str]) -> None:
    print(
        'Commands:\n'
        '  say <text>    - echo text\n'
        '  shout <text>  - echo text uppercased\n'
        '  help          - this message\n'
        '  exit          - quit'
    )


class ExitSignal(Exception):
    pass


def cmd_exit(_: ta.Sequence[str]) -> None:
    raise ExitSignal


COMMANDS: ta.Mapping[str, ta.Callable[[ta.Sequence[str]], ta.Any]] = {
    'say': cmd_say,
    'shout': cmd_shout,
    'help': cmd_help,
    'exit': cmd_exit,
}


##


if HAVE_READLINE:
    USING_LIBEDIT = 'libedit' in getattr(readline, '__doc__', '')

    ##

    HISTORY_FILE = '.mini_readline_repl_history'
    HISTORY_MAX = 1000

    # Load/save persistent history
    try:
        if os.path.exists(HISTORY_FILE):
            readline.read_history_file(HISTORY_FILE)
    except Exception:  # noqa
        pass

    atexit.register(lambda: (
        setattr(readline, 'set_history_length', getattr(readline, 'set_history_length', lambda *_: None)),
        readline.set_history_length(HISTORY_MAX) if hasattr(readline, 'set_history_length') else None,
        readline.write_history_file(HISTORY_FILE),
    ))

    ##

    # Key bindings: GNU readline vs libedit
    if USING_LIBEDIT:
        # libedit (macOS) uses a different syntax
        readline.parse_and_bind('bind ^I rl_complete')
        readline.parse_and_bind('bind -e')  # Emacs mode
    else:
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode emacs')

    # Make slash & dot part of filename tokens for nicer path completion but keep spaces and punctuation as delimiters.
    if hasattr(readline, 'set_completer_delims'):
        delims = readline.get_completer_delims()
        for ch in './-~':
            delims = delims.replace(ch, '')
        readline.set_completer_delims(delims)

    # Simple hybrid completer: commands first, then filesystem paths.
    def _path_candidates(prefix: str) -> ta.Iterator[str]:
        p = pathlib.Path(prefix or '.')
        base = p.parent if prefix and not prefix.endswith(os.sep) else p
        try:
            for entry in base.iterdir():
                s = str(entry if prefix.endswith(os.sep) else base / entry.name)
                yield s + (os.sep if entry.is_dir() else '')
        except Exception:  # noqa
            return

    def _command_candidates(prefix: str) -> ta.Iterator[str]:
        for c in COMMANDS:
            if c.startswith(prefix):
                yield c

    def completer(text, state):
        # Determine the current "word" being completed
        buf = readline.get_line_buffer()
        beg = readline.get_begidx()
        token = buf[beg:readline.get_endidx()]

        # If completing the first token, complete commands; otherwise filenames.
        parts = shlex.split(buf[:beg], posix=True)
        first = (len(parts) == 0)

        if first:
            candidates = list(_command_candidates(token))
        else:
            candidates = [c for c in _path_candidates(token) if c.startswith(token)]

        candidates.sort()
        return candidates[state] if state < len(candidates) else None

    readline.set_completer(completer)

    # Enable completion with TAB; also complete on first Tab (no double-Tab requirement)
    if not USING_LIBEDIT:
        readline.parse_and_bind('set show-all-if-ambiguous on')
        readline.parse_and_bind('set completion-ignore-case on')


##


ANSI_BOLD_CYAN = '\x1b[1;36m'
ANSI_RESET = '\x1b[0m'


def colored_prompt(txt: str) -> str:
    if HAVE_READLINE:
        # \x01 and \x02 mark non-printing spans for readline
        return f'\x01{ANSI_BOLD_CYAN}\x02{txt}\x01{ANSI_RESET}\x02'
    else:
        return f'{ANSI_BOLD_CYAN}{txt}{ANSI_RESET}'


PROMPT = colored_prompt('> ')


##


def _main() -> int:
    if not HAVE_READLINE:
        print('Note: GNU readline not available; using plain input().')

    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            print()  # newline after Ctrl-D
            break
        except KeyboardInterrupt:
            print()  # newline after Ctrl-C
            continue

        if not line.strip():
            continue

        try:
            parts = shlex.split(line, posix=True)
        except ValueError as e:
            print(f'Parse error: {e}')
            continue

        cmd, *args = parts
        impl = COMMANDS.get(cmd)
        if not impl:
            print(f"Unknown command: {cmd!r}. Try 'help'.")
            continue

        try:
            impl(args)
        except ExitSignal:
            break

    return 0


if __name__ == '__main__':
    raise SystemExit(_main())
