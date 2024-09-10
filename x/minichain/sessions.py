import dataclasses as dc

from .messages import Messages


##


@dc.dataclass(frozen=True)
class ChatSession:
    messages: Messages


@dc.dataclass(frozen=True)
class ChatSessionStore:
    store: dict[str, ChatSession] = dc.field(default_factory=dict)

    def get(self, session_id: str) -> ChatSession | None:
        return self.store.get(session_id)

    def put(self, session_id: str, session: ChatSession) -> None:
        self.store[session_id] = session


##


@dc.dataclass(frozen=True)
class ChatSessionAddition:
    messages: Messages
    session_id: str | None = None


@dc.dataclass(frozen=True)
class MessageHistoryChat:
    store: ChatSessionStore

    def invoke(self, new: ChatSessionAddition) -> Messages:
        if new.session_id is None:
            return new.messages

        session = self.store.get(new.session_id)
        if session is None:
            return new.messages

        return [
            *session.messages,
            *new.messages,
        ]


@dc.dataclass(frozen=True)
class UpdatingMessageHistoryChat(Invokable):
    child: Invokable
    store: ChatSessionStore

    def invoke(self, new: ChatSessionAddition) -> Messages:
        in_messages = MessageHistoryChat(self.store).invoke(new)

        out_message = self.child(in_messages)

        out_messages = [
            *in_messages,
            out_message,
        ]

        if new.session_id is not None:
            self.store.put(new.session_id, ChatSession(out_messages))

        return out_messages
