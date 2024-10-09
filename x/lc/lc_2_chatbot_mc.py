from ommlx.minichain.backends.openai import OpenaiChatModel
from ommlx.minichain.chat import AiMessage
from ommlx.minichain.chat import SystemMessage
from ommlx.minichain.chat import UserMessage
from ommlx.minichain.strings import transform_strings
from ommlx.minichain.templates import DictTemplater
from ommlx.minichain.templates import TemplatingModel

from x.lc.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    model = OpenaiChatModel(model="gpt-3.5-turbo")

    result = model([UserMessage("Hi! I'm Bob")])
    print(result)

    #

    result = model([UserMessage("What's my name?")])
    print(result)

    #

    result = model([
        UserMessage("Hi! I'm Bob"),
        AiMessage("Hello Bob! How can I assist you today?"),
        UserMessage("What's my name?"),
    ])
    print(result)


if __name__ == '__main__':
    _main()
