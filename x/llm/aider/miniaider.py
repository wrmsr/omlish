import os.path

import openai


MAIN_SYSTEM_PROMPT = """
You are an expert software engineer and pair programmer.

The user will show you source files in the following triple-quoted format.
NEVER REPLY USING THIS FORMAT!

dir0/dir1/example.py
```
class Foo:
    def mul(self, a: int, b: int) -> int:
        return a + b
```

Take requests from the user for information about the code, as well as to add new features, improvements, bug fixes and
other changes to the supplied code. If the user's request is ambiguous, ask questions to fully understand.
"""

REMINDER_SYSTEM_PROMPT = """
*NEVER REPLY WITH AN ENTIRE FILE TRIPLE-QUOTED FORMAT LIKE THE USER MESSAGES!*
"""

FILE_PROMPT_TEMPLATE = """
{name}
```
{content}
```
"""

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

    src_files = ['js/game_manager.js']

    files_content = []
    for src_file in src_files:
        with open(src_file) as f:
            content = f.read()
        files_content.append(FILE_PROMPT_TEMPLATE.format(
            name=src_file,
            content=content,
        ))

    user_input = 'What is this repo?'

    messages = [
        dict(role='system', content=MAIN_SYSTEM_PROMPT),
        dict(role='user', content='\n\n'.join(files_content)),
        dict(role='assistant', content='Ok.'),
        dict(role='system', content=REMINDER_SYSTEM_PROMPT),
        dict(role='user', content=user_input),
    ]

    resp = openai.chat.completions.create(
        messages=messages,
        model='gpt-4o',
    )

    print(resp.choices[0].message.content)


if __name__ == '__main__':
    _main()
