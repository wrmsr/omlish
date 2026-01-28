import asyncio
import threading

import transformers as tfm

from omlish.asyncs.asyncio.sync import AsyncioSyncBufferRelay

from ...streamers import CancellableTextStreamer


##


async def _a_main() -> None:
    model_name = 'meta-llama/Llama-3.2-1B-Instruct'  # Define the model name or path

    # Load the pre-trained model with automatic data type and device mapping
    model = tfm.AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype='auto',
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

    relay: AsyncioSyncBufferRelay = AsyncioSyncBufferRelay()

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
        await relay.wait()
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

        if 'Alibaba' in out:
            print('Canceling!')
            streamer.cancel()
            break

        if end:
            break

    thread.join()


if __name__ == '__main__':
    asyncio.run(_a_main())
