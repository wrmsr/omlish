from ommlx import minichain as mc
from ommlx.minichain.backends import openai as mc_oai

from x.lc.utils import load_secrets


def _main() -> None:
    load_secrets()

    model = mc_oai.OpenaiChatModel()
    messages: list[mc.Message] = []

    while True:
        line = input('>> ')
        messages.append(mc.UserMessage(line))

        ai = model(messages).v
        messages.append(ai)

        print(ai.s)


if __name__ == '__main__':
    _main()
