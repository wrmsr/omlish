from ommlx.minichain.backends.openai import OpenaiChatModel
from ommlx.minichain.chat import ChatRequest
from ommlx.minichain.chat import SystemMessage
from ommlx.minichain.chat import UserMessage
from ommlx.minichain.content import Text

from x.lc.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    model = OpenaiChatModel()

    messages = [
        SystemMessage('Translate the following from English into Italian'),
        UserMessage([Text("hi!")]),
    ]

    result = model.invoke(ChatRequest.new(messages))
    print(result)


if __name__ == '__main__':
    _main()
