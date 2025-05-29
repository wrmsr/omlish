import dataclasses as dc


##


@dc.dataclass()
class ChatToolCall:
    name: str
    arguments: str  # Arguments are stored as a JSON string
    id: str = ''    # Optional ID for the tool call


@dc.dataclass()
class ChatMsg:
    content: str = ''
    tool_calls: list[ChatToolCall] = dc.field(default_factory=list)
    reasoning_content: str = ''
