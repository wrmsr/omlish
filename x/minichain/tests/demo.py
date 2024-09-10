import contextlib
import os.path

import openai
import yaml

from ..completers import OpenaiChatCompleter
from ..messages import AiMessage
from ..messages import HumanMessage
from ..messages import SystemMessage
from ..parsers import StrMessageParser
from ..templaters import MessageTemplater


def _run_2_chatbot(client: openai.OpenAI) -> None:
    chat_completer = OpenaiChatCompleter(client, 'gpt-3.5-turbo')

    result = chat_completer.complete_chat([HumanMessage(content="Hi! I'm Bob")])
    print(result)

    #

    result = chat_completer.complete_chat([HumanMessage(content="What's my name?")])
    print(result)

    #

    result = chat_completer.complete_chat([
        HumanMessage(content="Hi! I'm Bob"),
        AiMessage(content='Hello Bob! How can I assist you today?'),
        HumanMessage(content="What's my name?"),
    ])
    print(result)


#


def _run_1_chain(client: openai.OpenAI) -> None:
    chat_completer = OpenaiChatCompleter(client, 'gpt-4')
    message_parser = StrMessageParser()

    #

    messages = [
        SystemMessage('Translate the following from English into Italian'),
        HumanMessage('hi!'),
    ]

    result = message_parser.parse_message(
        chat_completer.complete_chat(
            messages,
        ),
    )
    print(result)

    #

    message_templater = MessageTemplater([
        SystemMessage('Translate the following from English into {language}'),
        HumanMessage('{text}'),
    ])

    result = message_parser.parse_message(
        chat_completer.complete_chat(
            message_templater.template_messages({
                'language': 'Italian',
                'text': 'hi!',
            }),
        ),
    )
    print(result)


#


def _run(es: contextlib.ExitStack) -> None:
    client = es.enter_context(openai.OpenAI(
        api_key=os.environ['OPENAI_API_KEY'],
    ))

    #

    _run_1_chain(client)
    _run_2_chatbot(client)


#


def _load_secrets() -> None:
    with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
        dct = yaml.safe_load(f)
    os.environ['OPENAI_API_KEY'] = dct['openai_api_key']
    os.environ['TAVILY_API_KEY'] = dct['tavily_api_key']


def _main() -> None:
    _load_secrets()

    with contextlib.ExitStack() as es:
        _run(es)


if __name__ == '__main__':
    _main()
