import textwrap
import typing as ta

from omdev.home.secrets import load_secrets
from omlish import check
from ommlds import minichain as mc
from ommlds.minichain.backends.anthropic import AnthropicChatModel
from ommlds.minichain.backends.openai import OpenaiChatModel


def _main() -> None:
    sec = load_secrets()

    llm0 = OpenaiChatModel(api_key=sec.get('openai_api_key').reveal())
    llm1 = AnthropicChatModel(api_key=sec.get('anthropic_api_key').reveal())

    system_message = mc.SystemMessage(
        'You and the user are roleplaying as astronauts stuck on the moon. '
        'Your job is to work with the user to survive. '
        'You have only known the user for about a week, having only met before the beginning of your mission. '
    )

    messages: list[tuple[mc.Model, str]] = [
        (llm1, 'Hi! How are you?'),
    ]

    for _ in range(10):
        for llm in [llm0, llm1]:
            print(llm)
            print()
            resp = llm([
                system_message,
                *[
                    (mc.AiMessage if s is llm else mc.UserMessage)(m)
                    for s, m in messages
                ],
            ])
            rm = check.non_empty_str(resp.v[0].m.s)
            messages.append((llm, rm))
            print('\n'.join(textwrap.wrap(rm, 120)))
            print()


if __name__ == '__main__':
    _main()
