import threading
import time

import transformers as tfm


##


def _main() -> None:
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
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    # Set up the streamer for token generation
    streamer = tfm.TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    # Prepare model inputs by tokenizing the text and moving it to the model's device
    model_inputs = tokenizer([text], return_tensors='pt').to(model.device)

    # Set up generation arguments including max tokens and streamer
    generation_args = {
        'max_new_tokens': 512,
        'streamer': streamer,
        **model_inputs,
    }

    # Start a separate thread for model generation to allow streaming output1.10
    thread = threading.Thread(
        target=model.generate,
        kwargs=generation_args,
    )
    thread.start()

    # Accumulate and yield text tokens as they are generated
    acc_text = ''
    for text_token in streamer:
        time.sleep(0.01)  # Simulate real-time output with a short delay
        acc_text += text_token  # Append the generated token to the accumulated text
        print(acc_text)  # Yield the accumulated text

    # Ensure the generation thread completes
    thread.join()


if __name__ == '__main__':
    _main()
