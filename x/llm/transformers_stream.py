import asyncio
import threading
import time
import typing as ta

import transformers as tfm

from .stream.streamers import CancellableTextStreamer


T = ta.TypeVar('T')


##


class ThreadBufferRelay(ta.Generic[T]):
    def __init__(
            self,
            *,
            wake_fn: ta.Callable[[], None],
    ) -> None:
        super().__init__()

        self._wake_fn = wake_fn

        self._lock = threading.Lock()
        self._buffer: ThreadBufferRelay._Buffer = ThreadBufferRelay._Buffer()

    class _Buffer:
        def __init__(self) -> None:
            self.lst: list = []
            self.age = 0

        def __repr__(self) -> str:
            return f'{self.__class__.__qualname__}({self.lst!r}, age={self.age!r})'

    def push(self, *vs: T) -> None:
        with self._lock:
            buf = self._buffer
            needs_wake = not buf.age
            buf.lst.extend(vs)
            buf.age += 1
        if needs_wake:
            self._wake_fn()

    def swap(self) -> ta.Sequence[T]:
        with self._lock:
            buf, self._buffer = self._buffer, ThreadBufferRelay._Buffer()
        return buf.lst


##


async def _a_main() -> None:
    model_name = 'meta-llama/Llama-3.2-1B-Instruct'  # Define the model name or path

    # Load the pre-trained model with automatic data type and device mapping
    model = tfm.AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype='auto',
        device_map='auto',
    )

    # Load the tokenizer associated with the model
    tokenizer = tfm.AutoTokenizer.from_pretrained(model_name)

    message = 'Hi there'
    history: list = []

    # Construct the messages list with system, history, and user message
    messages = [
        {'role': 'system', 'content': 'You are Qwen, created by Alibaba Cloud. You are a helpful assistant.'},
    ]
    messages.extend(history)  # Add chat history to the messages list
    messages.append({'role': 'user', 'content': message})  # Append the user's message

    # Apply chat template to format the messages for the model
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    event = asyncio.Event()
    loop = asyncio.get_running_loop()
    relay = ThreadBufferRelay(
        wake_fn=lambda: loop.call_soon_threadsafe(event.set),  # noqa
    )

    def streamer_callback(text: str, *, stream_end: bool) -> None:
        if text or stream_end:
            relay.push(text, *([None] if stream_end else []))

    # Set up the streamer for token generation
    streamer = CancellableTextStreamer(
        tokenizer,
        streamer_callback,  # noqa
        skip_prompt=True,
        skip_special_tokens=True,
    )

    # Prepare model inputs by tokenizing the text and moving it to the model's device
    model_inputs = tokenizer([prompt], return_tensors='pt').to(model.device)

    # Set up generation arguments including max tokens and streamer
    generation_args = {
        'max_new_tokens': 512,
        'streamer': streamer,
        **model_inputs,
    }

    # Start a separate thread for model generation to allow streaming output1.10
    thread = threading.Thread(
        target=CancellableTextStreamer.ignoring_cancelled(model.generate),
        kwargs=generation_args,
    )
    thread.start()

    while True:
        await event.wait()
        event.clear()
        got = relay.swap()

        if not got:
            raise RuntimeError

        if got[-1] is None:
            out = ''.join(got[:-1])
            end = True
        else:
            out = ''.join(got)
            end = False

        print(out)
        if end:
            break

    thread.join()


if __name__ == '__main__':
    asyncio.run(_a_main())
