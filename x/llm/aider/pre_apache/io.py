import datetime
import os
import pathlib
import random
import time

from prompt_toolkit.completion import Completer
from prompt_toolkit.completion import Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token
from pygments.util import ClassNotFound
from rich.console import Console
from rich.text import Text


class _FileContentCompleter(Completer):
    def __init__(self, fnames, commands):
        super().__init__()

        self.commands = commands

        self.words = set()
        for fname in fnames:
            with open(fname) as f:
                content = f.read()

            try:
                lexer = guess_lexer_for_filename(fname, content)
            except ClassNotFound:
                continue

            tokens = list(lexer.get_tokens(content))  # noqa
            self.words.update(token[1] for token in tokens if token[0] in Token.Name)

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()
        if not words:
            return

        if text[0] == '/':
            if len(words) == 1 and not text[-1].isspace():
                candidates = self.commands.get_commands()
            else:
                for completion in self.commands.get_command_completions(
                    words[0][1:], words[-1],
                ):
                    yield completion
                return
        else:
            candidates = self.words

        last_word = words[-1]
        for word in candidates:
            if word.lower().startswith(last_word.lower()):
                yield Completion(word, start_position=-len(last_word))


class InputOutput:

    def __init__(
        self,
        pretty,
        yes,
        input_history_file,
        chat_history_file,
        input=None,  # noqa
        output=None,
    ):
        super().__init__()

        self._input = input
        self._output = output
        self._pretty = pretty
        self._yes = yes
        self._input_history_file = input_history_file
        self._chat_history_file = pathlib.Path(chat_history_file)

        if pretty:
            self._console = Console()
        else:
            self._console = Console(force_terminal=True, no_color=True)

        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._append_chat_history(f'\n# Aider chat started at {current_time}\n\n')

    def _canned_input(self, show_prompt):
        console = Console()

        input_line = input()

        console.print(show_prompt, end='', style='green')
        for char in input_line:
            console.print(char, end='', style='green')
            time.sleep(random.uniform(0.01, 0.15))
        console.print()
        console.print()
        return input_line

    def get_input(self, fnames, commands):
        if self._pretty:
            self._console.rule()
        else:
            print()

        fnames = list(fnames)
        if len(fnames) > 1:
            common_prefix = os.path.commonpath(fnames)
            if not common_prefix.endswith(os.path.sep):
                common_prefix += os.path.sep
            short_fnames = [fname.replace(common_prefix, '', 1) for fname in fnames]
        elif len(fnames):
            short_fnames = [os.path.basename(fnames[0])]
        else:
            short_fnames = []

        show = ' '.join(short_fnames)
        if len(show) > 10:
            show += '\n'
        show += '> '

        # if not sys.stdin.isatty():
        #    return self._canned_input(show)

        inp = ''
        multiline_input = False

        style = Style.from_dict({'': 'green'})

        while True:
            completer_instance = _FileContentCompleter(fnames, commands)
            if multiline_input:
                show = '. '

            session = PromptSession(
                message=show,
                completer=completer_instance,
                history=FileHistory(self._input_history_file),
                style=style,
                reserve_space_for_menu=4,
                complete_style=CompleteStyle.MULTI_COLUMN,
                input=self._input,
                output=self._output,
            )
            line = session.prompt()
            if line.strip() == '{' and not multiline_input:
                multiline_input = True
                continue
            if line.strip() == '}' and multiline_input:
                break
            elif multiline_input:
                inp += line + '\n'
            else:
                inp = line
                break

        print()

        prefix = '#### > '
        if inp:
            hist = inp.splitlines()
        else:
            hist = ['<blank>']

        hist = f'  \n{prefix} '.join(hist)

        hist = f"""
---
{prefix} {hist}"""
        self._append_chat_history(hist, linebreak=True)

        return inp

    # OUTPUT

    def ai_output(self, content):
        hist = '\n' + content.strip() + '\n\n'
        self._append_chat_history(hist)

    def confirm_ask(self, question, default='y'):
        if self._yes:
            res = 'yes'
        else:
            res = prompt(question + ' ', default=default)

        hist = f'{question.strip()} {res.strip()}'
        self._append_chat_history(hist, linebreak=True, blockquote=True)

        if not res or not res.strip():
            return None
        return res.strip().lower().startswith('y')

    def prompt_ask(self, question, default=None):
        if self._yes:
            res = 'yes'
        else:
            res = prompt(question + ' ', default=default)

        hist = f'{question.strip()} {res.strip()}'
        self._append_chat_history(hist, linebreak=True, blockquote=True)

        return res

    def tool_error(self, message):
        if message.strip():
            hist = f'{message.strip()}'
            self._append_chat_history(hist, linebreak=True, blockquote=True)

        message = Text(message)
        self._console.print(message, style='red')

    def tool(self, *messages):
        if messages:
            hist = ' '.join(messages)
            hist = f'{hist.strip()}'
            self._append_chat_history(hist, linebreak=True, blockquote=True)

        messages = list(map(Text, messages))
        self._console.print(*messages)

    def _append_chat_history(self, text, linebreak=False, blockquote=False):
        if blockquote:
            text = text.strip()
            text = '> ' + text
        if linebreak:
            text = text.rstrip()
            text = text + '  \n'
        if not text.endswith('\n'):
            text += '\n'
        with self._chat_history_file.open('a') as f:
            f.write(text)
