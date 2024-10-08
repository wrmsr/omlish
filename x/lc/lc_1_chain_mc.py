from ommlx.minichain.backends.openai import OpenaiChatModel
from ommlx.minichain.chat import ChatRequest
from ommlx.minichain.chat import SystemMessage
from ommlx.minichain.chat import UserMessage
from ommlx.minichain.content import Text
from ommlx.minichain.strings import transform_strings
from ommlx.minichain.templates import DictTemplater
from ommlx.minichain.templates import TemplatingModel

from x.lc.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    model = OpenaiChatModel()

    messages = [
        SystemMessage('Translate the following from English into Italian'),
        UserMessage.of('Hi!'),
    ]

    result = model(messages)
    print(result)

    #

    system_template = "Translate the following into {language}:"

    prompt_template = [
        SystemMessage(system_template),
        UserMessage.of("{text}"),
    ]

    templater = DictTemplater({"language": "italian", "text": "hi"})

    result = transform_strings(templater.apply, prompt_template)
    print(result)

    #

    model = TemplatingModel(model, templater)

    result = model(prompt_template)
    print(result)


if __name__ == '__main__':
    _main()
