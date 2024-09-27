#!/usr/bin/env python
"""
https://github.com/paul-gauthier/aider/blob/14f863e732ad69ebbea60b66fa692e2a5029f036/coder.py
"""
import argparse
import os
import pathlib
import re
import readline
import sys
import traceback
import typing as ta

import git
import openai
import openai.types.chat
from colorama import Fore
from colorama import Style
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.prompt import Prompt
from rich.text import Text
from tqdm import tqdm

from . import prompts
from .dump import dump


history_file = ".coder.history"
try:
    readline.read_history_file(history_file)
except FileNotFoundError:
    pass

openai.api_key = os.getenv("OPENAI_API_KEY")


def find_index(list1, list2):
    for i in range(len(list1)):
        if list1[i: i + len(list2)] == list2:
            return i
    return -1


Message: ta.TypeAlias = ta.Mapping[str, ta.Any]
CompletionChunk: ta.TypeAlias = openai.types.chat.ChatCompletionChunk


class Coder:

    def __init__(
            self,
            use_gpt_4,
            files,
            pretty,
    ) -> None:
        super().__init__()

        self._fnames: dict[str, float] = dict()
        self._last_modified = 0

        if use_gpt_4:
            self._main_model = "gpt-4"
        else:
            self._main_model = "gpt-3.5-turbo"

        for fname in files:
            self._fnames[fname] = pathlib.Path(fname).stat().st_mtime

        self.check_for_local_edits(True)

        self._pretty = pretty

        if pretty:
            self._console = Console()
        else:
            self._console = Console(force_terminal=True, no_color=True)

    def quoted_file(self, fname: str) -> str:
        prompt = "\n"
        prompt += fname
        prompt += "\n```\n"
        prompt += pathlib.Path(fname).read_text()
        prompt += "\n```\n"
        return prompt

    def get_files_content(self) -> str:
        prompt = ""
        for fname in self._fnames:
            prompt += self.quoted_file(fname)
        return prompt

    def get_input(self) -> str | None:
        if self._pretty:
            self._console.rule()
        else:
            print()

        inp = ""
        if self._pretty:
            print(Fore.GREEN, end="\r")
        else:
            print()

        while not inp.strip():
            try:
                inp = input("> ")
            except EOFError:
                return

        ###
        if self._pretty:
            print(Style.RESET_ALL)
        else:
            print()

        readline.write_history_file(history_file)
        return inp

    def check_for_local_edits(self, init: bool = False) -> bool | None:
        last_modified = max(pathlib.Path(fname).stat().st_mtime for fname in self._fnames)
        since = last_modified - self._last_modified
        self._last_modified = last_modified
        if init:
            return
        if since > 0:
            return True
        return False

    def get_files_messages(self) -> list[dict[str, ta.Any]]:
        files_content = prompts.FILES_CONTENT_PREFIX
        files_content += self.get_files_content()

        files_messages = [
            dict(role="user", content=files_content),
            dict(role="assistant", content="Ok."),
            dict(
                role="system",
                content=prompts.FILES_CONTENT_SUFFIX + prompts.SYSTEM_REMINDER,
            ),
        ]

        return files_messages

    _done_messages: list[Message]
    _cur_messages: list[Message]

    _num_control_c: int

    def run(self) -> None:
        self._done_messages = []
        self._cur_messages = []

        self._num_control_c = 0

        while True:
            try:
                self.run_loop()
            except KeyboardInterrupt:
                self._num_control_c += 1
                if self._num_control_c >= 2:
                    break
                self._console.print("[bold red]^C again to quit")

        if self._pretty:
            print(Style.RESET_ALL)

    def run_loop(self) -> bool | None:
        inp = self.get_input()
        if inp is None:
            return

        self._num_control_c = 0

        if self.check_for_local_edits():
            self.commit(ask=True)

            # files changed, move cur messages back behind the files messages
            self._done_messages += self._cur_messages
            self._done_messages += [
                dict(role="user", content=prompts.FILES_CONTENT_LOCAL_EDITS),
                dict(role="assistant", content="Ok."),
            ]
            self._cur_messages = []

        self._cur_messages += [
            dict(role="user", content=inp),
        ]

        messages = [
            dict(role="system", content=prompts.MAIN_SYSTEM + prompts.SYSTEM_REMINDER),
        ]
        messages += self._done_messages
        messages += self.get_files_messages()
        messages += self._cur_messages

        self.show_messages(messages, "all")

        content, interrupted = self.send(messages)
        if interrupted:
            content += "\n^C KeyboardInterrupt"

        pathlib.Path("tmp.last-edit.md").write_text(content)

        self._cur_messages += [
            dict(role="assistant", content=content),
        ]

        self._console.print()
        if interrupted:
            return True

        try:
            edited = self.update_files(content, inp)
        except Exception as err:
            print(err)
            print()
            traceback.print_exc()
            edited = None

        if not edited:
            return True

        res = self.commit(history=self._cur_messages)
        if res:
            commit_hash, commit_message = res

            saved_message = prompts.FILES_CONTENT_GPT_EDITS.format(
                hash=commit_hash,
                message=commit_message,
            )
        else:
            self._console.print('[red bold]Edits failed to change the files?')
            saved_message = prompts.FILES_CONTENT_GPT_NO_EDITS

        self.check_for_local_edits(True)
        self._done_messages += self._cur_messages
        self._done_messages += [
            dict(role="user", content=saved_message),
            dict(role="assistant", content="Ok."),
        ]
        self._cur_messages = []
        return True

    def show_messages(
            self,
            messages: ta.Iterable[Message],
            title: str,
    ) -> None:
        print(title.upper(), "*" * 50)

        for msg in messages:
            print()
            print("-" * 50)
            role = msg["role"].upper()
            content = msg["content"].splitlines()
            for line in content:
                print(role, line)

    _resp: str

    def send(
            self,
            messages: ta.Iterable[Message],
            model: str | None = None,
            progress_bar_expected: int = 0,
            silent: bool = False,
    ) -> tuple[str, bool]:
        # self.show_messages(messages, "all")

        if not model:
            model = self._main_model

        completion = openai.chat.completions.create(  # noqa
            model=model,
            messages=messages,
            temperature=0,
            stream=True,
        )

        interrupted = False
        try:
            if progress_bar_expected:
                self.show_send_progress(completion, progress_bar_expected)
            elif self._pretty and not silent:
                self.show_send_output_color(completion)
            else:
                self.show_send_output_plain(completion, silent)
        except KeyboardInterrupt:
            interrupted = True

        return self._resp, interrupted

    def show_send_progress(
            self,
            completion: ta.Iterable[CompletionChunk],
            progress_bar_expected: int,
    ) -> None:
        self._resp = ""
        pbar = tqdm(total=progress_bar_expected)
        for chunk in completion:
            try:
                text = chunk.choices[0].delta.content
                self._resp += text
            except AttributeError:
                continue

            pbar.update(len(text))

        pbar.update(progress_bar_expected)
        pbar.close()

    def show_send_output_plain(
            self,
            completion: ta.Iterable[CompletionChunk],
            silent: bool,
    ) -> None:
        self._resp = ""

        for chunk in completion:
            if chunk.choices[0].finish_reason not in (None, "stop"):
                dump(chunk.choices[0].finish_reason)
            try:
                text = chunk.choices[0].delta.content
                self._resp += text
            except AttributeError:
                continue

            if not silent:
                sys.stdout.write(text)
                sys.stdout.flush()

    def show_send_output_color(self, completion: ta.Iterable[CompletionChunk]) -> None:
        self._resp = ""

        with Live(vertical_overflow="scroll") as live:
            for chunk in completion:
                if chunk.choices[0].finish_reason not in (None, "stop"):
                    assert False, "Exceeded context window!"
                try:
                    text = chunk.choices[0].delta.content
                    if text is not None:
                        self._resp += text
                except AttributeError:
                    continue

                md = Markdown(self._resp, style="blue", code_theme="default")
                live.update(md)

            live.update(Text(""))
            live.stop()

        md = Markdown(self._resp, style="blue", code_theme="default")
        self._console.print(md)

    pattern: ta.ClassVar = re.compile(
        r"(^```\S*\s*)?^((?:[a-zA-Z]:\\|/)?(?:[\w\s.-]+[\\/])*\w+(\.\w+)?)\s+(^```\S*\s*)?^<<<<<<< ORIGINAL\n(.*?\n?)^=======\n(.*?)^>>>>>>> UPDATED",
        # noqa: E501
        re.MULTILINE | re.DOTALL,
    )

    def update_files(self, content: str, inp: str) -> set[str]:
        edited = set()
        for match in self.pattern.finditer(content):
            _, path, _, _, original, updated = match.groups()

            if path not in self._fnames:
                if not pathlib.Path(path).exists():
                    question = f"[red bold]Allow creation of new file {path}?"
                else:
                    question = f"[red bold]Allow edits to {path} which was not previously provided?"
                if not Confirm.ask(question, console=self._console):
                    self._console.print(f"[red]Skipping edit to {path}")
                    continue

                self._fnames[path] = 0

            edited.add(path)
            if self.do_replace(path, original, updated):
                continue
            edit = match.group()
            self.do_gpt_powered_replace(path, edit, inp)

        return edited

    def do_replace(self, fname: str, before_text: str, after_text: str) -> bool | None:
        before_text = self.strip_quoted_wrapping(before_text, fname)
        after_text = self.strip_quoted_wrapping(after_text, fname)

        fname = pathlib.Path(fname)

        # does it want to make a new file?
        if not fname.exists() and not before_text:
            print("Creating empty file:", fname)
            fname.touch()

        content = fname.read_text().splitlines()

        if not before_text and not content:
            # first populating an empty file
            new_content = after_text
        else:
            before_lines = [line.strip() for line in before_text.splitlines()]
            stripped_content = [line.strip() for line in content]
            where = find_index(stripped_content, before_lines)

            if where < 0:
                return

            new_content = content[:where]
            new_content += after_text.splitlines()
            new_content += content[where + len(before_lines):]
            new_content = "\n".join(new_content) + "\n"

        fname.write_text(new_content)
        self._console.print(f"[red]Applied edit to {fname}")
        return True

    def do_gpt_powered_replace(self, fname: str, edit: str, request: str) -> None:
        model = "gpt-3.5-turbo"
        print(f"Asking {model} to apply ambiguous edit to {fname}...")

        fname = pathlib.Path(fname)
        content = fname.read_text()
        prompt = prompts.EDITOR_USER.format(
            request=request,
            edit=edit,
            fname=fname,
            content=content,
        )

        messages = [
            dict(role="system", content=prompts.EDITOR_SYSTEM),
            dict(role="user", content=prompt),
        ]
        res, interrupted = self.send(
            messages, progress_bar_expected=len(content) + len(edit) / 2, model=model
        )
        if interrupted:
            return

        res = self.strip_quoted_wrapping(res, fname)
        fname.write_text(res)

    def strip_quoted_wrapping(self, res: str, fname: pathlib.Path | str | None = None) -> str:
        if not res:
            return res

        res = res.splitlines()

        if fname and res[0].strip().endswith(pathlib.Path(fname).name):
            res = res[1:]

        if res[0].startswith("```") and res[-1].startswith("```"):
            res = res[1:-1]

        res = "\n".join(res)
        if res and res[-1] != "\n":
            res += "\n"

        return res

    def commit(
            self,
            history=None,
            prefix=None,
            ask=False,
    ):
        repo_paths = set(
            git.Repo(fname, search_parent_directories=True).git_dir
            for fname in self._fnames
        )

        if len(repo_paths) > 1:
            repo_paths = " ".join(repo_paths)
            raise ValueError(f"Files must all be in one git repo, not: {repo_paths}")

        repo = git.Repo(repo_paths.pop())
        if not repo.is_dirty():
            return

        diffs = ''
        dirty_fnames = []
        relative_dirty_fnames = []
        for fname in self._fnames:
            relative_fname = os.path.relpath(fname, repo.working_tree_dir)
            these_diffs = repo.git.diff("HEAD", relative_fname)
            if these_diffs:
                dirty_fnames.append(fname)
                relative_dirty_fnames.append(relative_fname)
                diffs += these_diffs + "\n"

        if not dirty_fnames:
            return

        self._console.print(Text(diffs))

        diffs = "# Diffs:\n" + diffs

        # for fname in dirty_fnames:
        #    self._console.print(f"[red]  {fname}")

        context = ""
        if history:
            context += "# Context:\n"
            for msg in history:
                context += msg["role"].upper() + ": " + msg["content"] + "\n"

        messages = [
            dict(role="system", content=prompts.COMMIT_SYSTEM),
            dict(role="user", content=context + diffs),
        ]

        if history:
            self.show_messages(messages, "commit")

        commit_message, interrupted = self.send(
            messages,
            model="gpt-3.5-turbo",
            silent=True,
        )

        commit_message = commit_message.strip().strip('"').strip()

        if interrupted:
            raise KeyboardInterrupt

        if prefix:
            commit_message = prefix + commit_message

        self._console.print("[red]Files have uncommitted changes.\n")
        self._console.print(f"[red]Suggested commit message:\n{commit_message}\n")

        if ask:
            res = Prompt.ask("[red]Commit before the chat proceeds? [y/n/commit message]").strip()

            if res.lower() in ['n', 'no']:
                self._console.print("[red]Skipped commmit.")
                return
            if res.lower() not in ['y', 'yes']:
                commit_message = res

        repo.git.add(*relative_dirty_fnames)
        commit_result = repo.git.commit("-m", commit_message, "--no-verify")
        commit_hash = repo.head.commit.hexsha[:7]
        self._console.print(f"[green]{commit_hash} {commit_message}")
        return commit_hash, commit_message


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with GPT about code")
    parser.add_argument(
        "files", metavar="FILE", nargs="+", help="a list of source code files"
    )
    parser.add_argument(
        "-3",
        "--gpt-3-5-turbo",
        action="store_true",
        help="Only use gpt-3.5-turbo, not gpt-4",
    )
    parser.add_argument(
        "--no-pretty",
        action="store_false",
        dest="pretty",
        default=True,
        help="Disable prettyd output of GPT responses",
    )
    parser.add_argument(
        "--apply",
        metavar="FILE",
        help="Apply the changes from the given file instead of running the chat",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit dirty files without confirmation",
    )

    args = parser.parse_args()

    with open(os.path.expanduser('~/.omlish-llm/.env')) as f:
        os.environ.update({
            k: v
            for l in f
            if (s := l.strip())
            for k, v in [s.split('=')]
        })

    use_gpt_4 = not args.gpt_3_5_turbo
    fnames = args.files
    pretty = args.pretty

    coder = Coder(use_gpt_4, fnames, pretty)
    coder.commit(ask=not args.commit, prefix="WIP: ")

    if args.apply:
        with open(args.apply, "r") as f:
            content = f.read()
        coder.update_files(content, inp="")
        return

    coder.run()


if __name__ == "__main__":
    status = main()
    sys.exit(status)
