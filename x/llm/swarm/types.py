from openai.types.chat import ChatCompletionMessage  # noqa
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall  # noqa
from openai.types.chat.chat_completion_message_tool_call import Function  # noqa
from collections.abc import Callable
from typing import Union

# Third-party imports
from pydantic import BaseModel


AgentFunction = Callable[[], Union[str, 'Agent', dict]]


class Agent(BaseModel):
    name: str = 'Agent'
    model: str = 'gpt-4o'
    instructions: str | Callable[[], str] = 'You are a helpful agent.'
    functions: list[AgentFunction] = []
    tool_choice: str = None
    parallel_tool_calls: bool = True


class Response(BaseModel):
    messages: list = []
    agent: Agent | None = None
    context_variables: dict = {}


class Result(BaseModel):
    """
    Encapsulates the possible return values for an agent function.

    Attributes:
        value (str): The result value as a string.
        agent (Agent): The agent instance, if applicable.
        context_variables (dict): A dictionary of context variables.
    """

    value: str = ''
    agent: Agent | None = None
    context_variables: dict = {}
