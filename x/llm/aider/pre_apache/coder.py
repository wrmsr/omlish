import os
import sys
import time
import traceback
import pathlib

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
import git
import openai

from . import prompts
from . import utils
from .commands import Commands


class Coder:

    def __init__(
            self,
            main_model,
            fnames,
            pretty,
            show_diffs,
            auto_commits,
            io,
            dry_run,
    ):
        super().__init__()

        self._abs_fnames = set()

        self._io = io

        self._auto_commits = auto_commits
        self._dry_run = dry_run

        if pretty:
            self._console = Console()
        else:
            self._console = Console(force_terminal=True, no_color=True)

        self._done_messages = []
        self._cur_messages = []

        self._num_control_c = 0

        self._last_aider_commit_hash = None
        self._last_asked_for_commit_time = 0

        self._commands = Commands(self._io, self)
        self._main_model = main_model
        if main_model == 'gpt-3.5-turbo':
            self._io.tool_error(f"Aider doesn't work well with {main_model}, use gpt-4 for best results.")

        self._repo = None
        self._set_repo(fnames)

        if not self._repo:
            self._io.tool_error(
                'No suitable git repo, will not automatically commit edits.',
            )
            self._find_common_root()

        self._pretty = pretty
        self._show_diffs = show_diffs

    @property
    def cur_messages(self):
        return self._cur_messages

    @property
    def last_aider_commit_hash(self):
        return self._last_aider_commit_hash

    @property
    def pretty(self):
        return self._pretty

    @property
    def repo(self):
        return self._repo

    @property
    def root(self):
        return self._root

    @property
    def abs_fnames(self):
        return self._abs_fnames

    def _find_common_root(self):
        if self._abs_fnames:
            common_prefix = os.path.commonpath(list(self._abs_fnames))
            self._root = os.path.dirname(common_prefix)
        else:
            self._root = os.getcwd()

        self._io.tool(f'Common root directory: {self._root}')

    def _set_repo(self, cmd_line_fnames):
        if not cmd_line_fnames:
            cmd_line_fnames = ['.']

        repo_paths = []
        for fname in cmd_line_fnames:
            fname = pathlib.Path(fname)
            if not fname.exists():
                self._io.tool(f'Creating empty file {fname}')
                fname.parent.mkdir(parents=True, exist_ok=True)
                fname.touch()

            try:
                repo_path = git.Repo(fname, search_parent_directories=True).git_dir
                repo_paths.append(repo_path)
            except git.exc.InvalidGitRepositoryError:
                pass

            if fname.is_dir():
                continue

            self._io.tool(f'Added {fname} to the chat')

            fname = fname.resolve()
            self._abs_fnames.add(str(fname))

        num_repos = len(set(repo_paths))

        if num_repos == 0:
            self._io.tool_error('Files are not in a git repo.')
            return
        if num_repos > 1:
            self._io.tool_error('Files are in different git repos.')
            return

        # https://github.com/gitpython-developers/GitPython/issues/427
        repo = git.Repo(repo_paths.pop(), odbt=git.GitDB)  # noqa

        self._root = repo.working_tree_dir

        new_files = []
        for fname in self._abs_fnames:
            relative_fname = self._get_rel_fname(fname)
            tracked_files = set(repo.git.ls_files().splitlines())
            if relative_fname not in tracked_files:
                new_files.append(relative_fname)

        if new_files:
            rel_repo_dir = os.path.relpath(repo.git_dir, os.getcwd())

            self._io.tool(f'Files not tracked in {rel_repo_dir}:')
            for fn in new_files:
                self._io.tool(f' - {fn}')
            if self._io.confirm_ask('Add them?'):
                for relative_fname in new_files:
                    repo.git.add(relative_fname)
                    self._io.tool(f'Added {relative_fname} to the git repo')
                show_files = ', '.join(new_files)
                commit_message = f'Added new files to the git repo: {show_files}'
                repo.git.commit('-m', commit_message, '--no-verify')
                commit_hash = repo.head.commit.hexsha[:7]
                self._io.tool(f'Commit {commit_hash} {commit_message}')
            else:
                self._io.tool_error('Skipped adding new files to the git repo.')
                return

        self._repo = repo

    def _get_files_content(self, fnames=None):
        if not fnames:
            fnames = self._abs_fnames

        prompt = ''
        for fname in fnames:
            relative_fname = self._get_rel_fname(fname)
            prompt += utils.quoted_file(fname, relative_fname)
        return prompt

    def _get_files_messages(self):
        files_content = prompts.files_content_prefix
        files_content += self._get_files_content()

        all_content = files_content

        if self._repo is not None:
            tracked_files = set(self._repo.git.ls_files().splitlines())
            files_listing = '\n'.join(tracked_files)
            repo_content = prompts.repo_content_prefix
            repo_content += files_listing

            all_content = repo_content + '\n\n' + files_content

        files_messages = [
            dict(role='user', content=all_content),
            dict(role='assistant', content='Ok.'),
            dict(
                role='system',
                content=prompts.files_content_suffix + prompts.system_reminder,
            ),
        ]

        return files_messages

    def run(self):
        self._done_messages = []
        self._cur_messages = []

        self._num_control_c = 0

        while True:
            try:
                new_user_message = self._run_loop()
                while new_user_message:
                    new_user_message = self._send_new_user_message(new_user_message)

            except KeyboardInterrupt:
                self._num_control_c += 1
                if self._num_control_c >= 2:
                    break
                self._io.tool_error('^C again to quit')
            except EOFError:
                return

    def _should_auto_commit(self, inp):
        is_commit_command = inp and inp.startswith('/commit')

        if not self._auto_commits:
            return None
        if not self._repo:
            return None
        if not self._repo.is_dirty():
            return None
        if is_commit_command:
            return None
        if self._last_asked_for_commit_time >= self._get_last_modified():
            return None
        return True

    def _run_loop(self):
        inp = self._io.get_input(self._abs_fnames, self._commands)

        self._num_control_c = 0

        if self._should_auto_commit(inp):
            self.commit(ask=True, which='repo_files')

            # files changed, move cur messages back behind the files messages
            self._done_messages += self._cur_messages
            self._done_messages += [
                dict(role='user', content=prompts.files_content_local_edits),
                dict(role='assistant', content='Ok.'),
            ]
            self._cur_messages = []

        if not inp:
            return None

        if inp.startswith('/'):
            return self._commands.run(inp)

        return self._send_new_user_message(inp)

    def _send_new_user_message(self, inp):
        self._cur_messages += [
            dict(role='user', content=inp),
        ]

        messages = [
            dict(role='system', content=prompts.main_system + prompts.system_reminder),
        ]
        messages += self._done_messages
        messages += self._get_files_messages()
        messages += self._cur_messages

        # utils.show_messages(messages, "all")

        content, interrupted = self._send(messages)
        if interrupted:
            self._io.tool_error('\n\n^C KeyboardInterrupt')
            content += '\n^C KeyboardInterrupt'

        self._cur_messages += [
            dict(role='assistant', content=content),
        ]

        self._io.tool()
        if interrupted:
            return None

        edited, edit_error = self._apply_updates(content, inp)
        if edit_error:
            return edit_error

        if edited and self._auto_commits:
            self._auto_commit()

        add_rel_files_message = self._check_for_file_mentions(content)
        if add_rel_files_message:
            return add_rel_files_message

    def _auto_commit(self):
        res = self.commit(history=self._cur_messages, prefix='aider: ')
        if res:
            commit_hash, commit_message = res
            self._last_aider_commit_hash = commit_hash

            saved_message = prompts.files_content_gpt_edits.format(
                hash=commit_hash,
                message=commit_message,
            )
        else:
            # TODO: if not self.repo then the files_content_gpt_no_edits isn't appropriate
            self._io.tool_error('Warning: no changes found in tracked files.')
            saved_message = prompts.files_content_gpt_no_edits

        self._done_messages += self._cur_messages
        self._done_messages += [
            dict(role='user', content=saved_message),
            dict(role='assistant', content='Ok.'),
        ]
        self._cur_messages = []

    def _check_for_file_mentions(self, content):
        words = set(word for word in content.split())

        # drop sentence punctuation from the end
        words = set(word.rstrip(',.!;') for word in words)

        # strip away all kinds of quotes
        quotes = ''.join(['"', "'", '`'])
        words = set(word.strip(quotes) for word in words)

        addable_rel_fnames = set(self.get_all_relative_files()) - set(
            self.get_inchat_relative_files(),
        )

        mentioned_rel_fnames = set()
        for word in words:
            if word in addable_rel_fnames:
                mentioned_rel_fnames.add(word)

        if not mentioned_rel_fnames:
            return None

        for rel_fname in mentioned_rel_fnames:
            self._io.tool(rel_fname)

        if not self._io.confirm_ask('Add these files to the chat?'):
            return None

        for rel_fname in mentioned_rel_fnames:
            self._abs_fnames.add(os.path.abspath(os.path.join(self._root, rel_fname)))

        return prompts.added_files.format(fnames=', '.join(mentioned_rel_fnames))

    def _send(self, messages, model=None, silent=False):
        if not model:
            model = self._main_model

        class RateLimitError(Exception):
            pass

        self.resp = ''
        interrupted = False
        try:
            while True:
                try:
                    completion = openai.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0,
                        stream=True,
                    )
                    break
                except RateLimitError:
                    retry_after = 1
                    # print(f"Rate limit exceeded. Retrying in {retry_after} seconds.")
                    time.sleep(retry_after)

            self._show_send_output(completion, silent)
        except KeyboardInterrupt:
            interrupted = True

        if not silent:
            self._io.ai_output(self.resp)

        return self.resp, interrupted

    def _show_send_output(self, completion, silent):
        live = None
        if self._pretty and not silent:
            live = Live(vertical_overflow='scroll')  # noqa

        try:
            if live:
                live.start()

            for chunk in completion:
                if chunk.choices[0].finish_reason not in (None, 'stop'):
                    assert False, 'Exceeded context window!'

                try:
                    text = chunk.choices[0].delta.content
                    if text is not None:
                        self.resp += text
                except AttributeError:
                    continue

                if silent:
                    continue

                if self._pretty:
                    md = Markdown(self.resp, style='blue', code_theme='default')
                    live.update(md)
                else:
                    sys.stdout.write(text)
                    sys.stdout.flush()
        finally:
            if live:
                live.stop()

    def update_files(self, content, inp):  # noqa
        # might raise ValueError for malformed ORIG/UPD blocks
        edits = list(utils.find_original_update_blocks(content))

        edited = set()
        for path, original, updated in edits:
            full_path = os.path.abspath(os.path.join(self._root, path))

            if full_path not in self._abs_fnames:
                if not pathlib.Path(full_path).exists():
                    question = f'Allow creation of new file {path}?'  # noqa: E501
                else:
                    question = f'Allow edits to {path} which was not previously provided?'  # noqa: E501
                if not self._io.confirm_ask(question):
                    self._io.tool_error(f'Skipping edit to {path}')
                    continue

                if not pathlib.Path(full_path).exists():
                    pathlib.Path(full_path).parent.mkdir(parents=True, exist_ok=True)
                    pathlib.Path(full_path).touch()

                self._abs_fnames.add(full_path)

                # Check if the file is already in the repo
                if self._repo:
                    tracked_files = set(self._repo.git.ls_files().splitlines())
                    relative_fname = self._get_rel_fname(full_path)
                    if relative_fname not in tracked_files and self._io.confirm_ask(
                        f'Add {path} to git?',
                    ):
                        self._repo.git.add(full_path)

            edited.add(path)
            if utils.do_replace(full_path, original, updated, self._dry_run):
                if self._dry_run:
                    self._io.tool(f'Dry run, did not apply edit to {path}')
                else:
                    self._io.tool(f'Applied edit to {path}')
            else:
                self._io.tool_error(f'Failed to apply edit to {path}')

        return edited

    def _get_context_from_history(self, history):
        context = ''
        if history:
            context += '# Context:\n'
            for msg in history:
                context += msg['role'].upper() + ': ' + msg['content'] + '\n'
        return context

    def _get_commit_message(self, diffs, context):
        diffs = '# Diffs:\n' + diffs

        messages = [
            dict(role='system', content=prompts.commit_system),
            dict(role='user', content=context + diffs),
        ]

        commit_message, interrupted = self._send(
            messages,
            model='gpt-3.5-turbo',
            silent=True,
        )

        commit_message = commit_message.strip().strip('"').strip()

        if interrupted:
            self._io.tool_error(
                'Unable to get commit message from gpt-3.5-turbo. Use /commit to try again.',
            )
            return None

        return commit_message

    def commit(
            self,
            history=None,
            prefix=None,
            ask=False,
            message=None,
            which='chat_files',
    ):
        repo = self._repo
        if not repo:
            return None

        if not repo.is_dirty():
            return None

        def get_dirty_files_and_diffs(file_list):
            diffs = ''  # noqa
            relative_dirty_files = []
            for fname in file_list:
                relative_fname = self._get_rel_fname(fname)
                relative_dirty_files.append(relative_fname)

                try:
                    current_branch_commit_count = len(
                        list(repo.iter_commits(repo.active_branch)),
                    )
                except git.exc.GitCommandError:
                    current_branch_commit_count = None

                if not current_branch_commit_count:
                    continue

                if self._pretty:
                    these_diffs = repo.git.diff('HEAD', '--color', '--', relative_fname)
                else:
                    these_diffs = repo.git.diff('HEAD', relative_fname)

                if these_diffs:
                    diffs += these_diffs + '\n'

            return relative_dirty_files, diffs

        if which == 'repo_files':
            all_files = [
                os.path.join(self._root, f) for f in self.get_all_relative_files()
            ]
            relative_dirty_fnames, diffs = get_dirty_files_and_diffs(all_files)
        elif which == 'chat_files':
            relative_dirty_fnames, diffs = get_dirty_files_and_diffs(self._abs_fnames)
        else:
            raise ValueError(f"Invalid value for 'which': {which}")

        if self._show_diffs or ask:
            # don't use io.tool() because we don't want to log or further colorize
            print(diffs)

        context = self._get_context_from_history(history)
        if message:
            commit_message = message
        else:
            commit_message = self._get_commit_message(diffs, context)

        if prefix:
            commit_message = prefix + commit_message

        if ask:
            if which == 'repo_files':
                self._io.tool('Git repo has uncommitted changes.')
            else:
                self._io.tool('Files have uncommitted changes.')

            res = self._io.prompt_ask(
                'Commit before the chat proceeds [y/n/commit message]?',
                default=commit_message,
            ).strip()
            self._last_asked_for_commit_time = self._get_last_modified()

            self._io.tool()

            if res.lower() in ['n', 'no']:
                self._io.tool_error('Skipped commit.')
                return None
            if res.lower() not in ['y', 'yes'] and res:
                commit_message = res

        repo.git.add(*relative_dirty_fnames)

        full_commit_message = commit_message + '\n\n' + context
        repo.git.commit('-m', full_commit_message, '--no-verify')
        commit_hash = repo.head.commit.hexsha[:7]
        self._io.tool(f'Commit {commit_hash} {commit_message}')

        return commit_hash, commit_message

    def _get_rel_fname(self, fname):
        return os.path.relpath(fname, self._root)

    def get_inchat_relative_files(self):
        files = [self._get_rel_fname(fname) for fname in self._abs_fnames]
        return sorted(set(files))

    def get_all_relative_files(self):
        if self._repo:
            files = self._repo.git.ls_files().splitlines()
        else:
            files = self.get_inchat_relative_files()

        return sorted(set(files))

    def _get_all_abs_files(self):
        files = self.get_all_relative_files()
        files = [os.path.abspath(os.path.join(self._root, path)) for path in files]
        return files

    def _get_last_modified(self):
        files = self._get_all_abs_files()
        if not files:
            return 0
        return max(pathlib.Path(path).stat().st_mtime for path in files)

    def _apply_updates(self, content, inp):
        try:
            edited = self.update_files(content, inp)
            return edited, None
        except ValueError as err:
            err = err.args[0]
            self._io.tool_error('Malformed ORIGINAL/UPDATE blocks, retrying...')
            self._io.tool_error(str(err))
            return None, err

        except Exception as err:
            print(err)
            print()
            traceback.print_exc()
            return None, err
