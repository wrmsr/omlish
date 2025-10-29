# https://github.com/karpathy/nanochat/tree/9467d83cf23dcc9a9b4ca6e35103142f48a55b27

---

# rustbpe

> The missing tiktoken training code

A very lightweight Rust library for training a GPT tokenizer. The issue is that the inference library [tiktoken](https://github.com/openai/tiktoken) is great, but only does inference. Separately, the huggingface [tokenizers](https://github.com/huggingface/tokenizers) library does training, but it is rather bloated and really hard to navigate because it has to support all the different historical baggage of how people dealt with tokenizers over the years. More recently, I also wrote the [minbpe](https://github.com/karpathy/minbpe) library which does both training and inference, but only in inefficient Python. Basically what I really want is a non-fancy, super simple, but still relatively efficient training code for GPT tokenizer (more efficient than minbpe, much cleaner/simpler than tokenizers), and then export the trained vocab for inference with tiktoken. Does that make sense? So here we are. There are more opportunities for optimization here, I just stopped a bit early because unlike minbpe before it, rustbpe is now simple and fast enough, and not a significant bottleneck for nanochat.
