"""
TODO (immed):
 - -c / chat mode

==

https://platform.openai.com/usage
https://platform.openai.com/settings/organization/billing/overview

==

PATH="/usr/local/cuda-12.2/bin:$PATH"
JIT=1
GPU=1
PYTHONPATH=tinygrad
./python
tinygrad/examples/llama.py
--model /raid/huggingface/hub/models--huggyllama--llama-7b/snapshots/8416d3fefb0cb3ff5775a7b13c1692d10ff1aa16/model.safetensors.index.json
--prompt 'hi'
"""
import argparse
import dataclasses as dc
import datetime
import os.path
import sys

from dp.utils import load_secrets
from omlish import logs
from omlish.diag import pycharm

from .chat import Chat
from .chat import ChatMessage
from .chat import ChatRole
from .state import load_state
from .state import save_state


##


def _main() -> None:
    logs.configure_standard_logging('INFO')

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('prompt')
    parser.add_argument('-c', '--chat', action='store_true')
    parser.add_argument('-n', '--new', action='store_true')
    args = parser.parse_args()

    args.new = True

    #

    prompt = args.prompt

    if not sys.stdin.isatty() and not pycharm.is_pycharm_hosted():
        stdin_data = sys.stdin.read()
        prompt = '\n'.join([prompt, stdin_data])

    #

    state_dir = os.path.expanduser('~/.omlish-llm')
    if not os.path.exists(state_dir):
        os.mkdir(state_dir)
        os.chmod(state_dir, 0o770)

    chat_file = os.path.join(state_dir, 'chat.json')
    if args.new:
        chat = Chat()
    else:
        chat = load_state(chat_file, Chat)
        if chat is None:
            chat = Chat()

    #

    chat = dc.replace(
        chat,
        messages=[
            *chat.messages,
            ChatMessage(ChatRole.USER, prompt),
        ],
    )


    #

    load_secrets()

    #

    use_chat = True

    if use_chat:
        # llm = OpenaiChatLlm()
        llm = LlamacppChatLlm()

        response = llm.get_completion(chat.messages)

    else:
        DELIM = '\n\n====\n\n'

        full_prompt = DELIM.join(m.text for m in chat.messages)

        # sys.stdout.write(full_prompt)
        # sys.stdout.write(DELIM)

        #

        # llm = OpenaiPromptLlm()
        # llm = LlamacppPromptLlm()
        llm = TransformersPromptLlm()

        response = llm.get_completion(full_prompt).strip()

    print(response)

    chat = dc.replace(
        chat,
        messages=[
            *chat.messages,
            ChatMessage(ChatRole.ASSISTANT, response),
        ],
    )

    #

    chat = dc.replace(
        chat,
        updated_at=datetime.datetime.now(),
    )

    save_state(chat_file, chat, Chat)


if __name__ == '__main__':
    _main()
