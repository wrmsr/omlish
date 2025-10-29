# https://github.com/karpathy/nanochat/tree/9467d83cf23dcc9a9b4ca6e35103142f48a55b27
"""
BPE Tokenizer in the style of GPT-4.

Two implementations are available:
1) HuggingFace Tokenizer that can do both training and inference but is really confusing
2) Our own RustBPE Tokenizer for training and tiktoken for efficient inference
"""
import copy
import os
import pickle
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import lang


with lang.auto_proxy_import(globals()):
    import tiktoken
    import tokenizers


rustbpe: ta.Any = lang.proxy_import('.rustbpe', __package__)


##


SPECIAL_TOKENS = [
    # every document begins with the Beginning of Sequence (BOS) token that delimits documents
    '<|bos|>',
    # tokens below are only used during finetuning to render Conversations into token ids
    '<|user_start|>',  # user messages
    '<|user_end|>',
    '<|assistant_start|>',  # assistant messages
    '<|assistant_end|>',
    '<|python_start|>',  # assistant invokes python REPL tool
    '<|python_end|>',
    '<|output_start|>',  # python REPL outputs back to assistant
    '<|output_end|>',
]


# NOTE: this split pattern deviates from GPT-4 in that we use \p{N}{1,2} instead of \p{N}{1,3}
# I did this because I didn't want to "waste" too many tokens on numbers for smaller vocab sizes.
# I haven't validated that this is actually a good idea, TODO.
SPLIT_PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,2}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""  # noqa


# -----------------------------------------------------------------------------
# Generic GPT-4-style tokenizer based on HuggingFace Tokenizer


class HuggingFaceTokenizer:
    """Light wrapper around HuggingFace Tokenizer for some utilities"""

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    @classmethod
    def from_pretrained(cls, hf_path):
        # init from a HuggingFace pretrained tokenizer (e.g. "gpt2")
        tokenizer = tokenizers.Tokenizer.from_pretrained(hf_path)
        return cls(tokenizer)

    @classmethod
    def from_directory(cls, tokenizer_dir):
        # init from a local directory on disk (e.g. "out/tokenizer")
        tokenizer_path = os.path.join(tokenizer_dir, 'tokenizer.json')
        tokenizer = tokenizers.Tokenizer.from_file(tokenizer_path)
        return cls(tokenizer)

    @classmethod
    def train_from_iterator(
            cls,
            text_iterator,
            vocab_size,
            *,
            split_pattern=SPLIT_PATTERN,
            special_tokens=SPECIAL_TOKENS,
    ):
        # train from an iterator of text
        # Configure the HuggingFace Tokenizer
        tokenizer = tokenizers.Tokenizer(tokenizers.models.BPE(
            byte_fallback=True,  # needed!
            unk_token=None,
            fuse_unk=False,
        ))
        # Normalizer: None
        tokenizer.normalizer = None
        # Pre-tokenizer: GPT-4 style
        # the regex pattern used by GPT-4 to split text into groups before BPE
        # NOTE: The pattern was changed from \p{N}{1,3} to \p{N}{1,2} because I suspect it is harmful to
        # very small models and smaller vocab sizes, because it is a little bit wasteful in the token space.
        # (but I haven't validated this! TODO)
        gpt4_split_regex = tokenizers.Regex(split_pattern)  # huggingface demands that you wrap it in Regex!!
        tokenizer.pre_tokenizer = tokenizers.pre_tokenizers.Sequence([
            tokenizers.pre_tokenizers.Split(pattern=gpt4_split_regex, behavior='isolated', invert=False),
            tokenizers.pre_tokenizers.ByteLevel(add_prefix_space=False, use_regex=False),
        ])
        # Decoder: ByteLevel (it pairs together with the ByteLevel pre-tokenizer)
        tokenizer.decoder = tokenizers.decoders.ByteLevel()
        # Post-processor: None
        tokenizer.post_processor = None
        # Trainer: BPE
        trainer = tokenizers.trainers.BpeTrainer(
            vocab_size=vocab_size,
            show_progress=True,
            min_frequency=0,  # no minimum frequency
            initial_alphabet=tokenizers.pre_tokenizers.ByteLevel.alphabet(),
            special_tokens=special_tokens,
        )
        # Kick off the training
        tokenizer.train_from_iterator(text_iterator, trainer)
        return cls(tokenizer)

    def encode_ordinary(self, text):
        ids = self.tokenizer.encode(text, add_special_tokens=False).ids
        return ids

    def get_vocab_size(self):
        return self.tokenizer.get_vocab_size()

    def get_special_tokens(self):
        special_tokens_map = self.tokenizer.get_added_tokens_decoder()
        special_tokens = [w.content for w in special_tokens_map.values()]
        return special_tokens

    def id_to_token(self, id):  # noqa
        return self.tokenizer.id_to_token(id)

    def _encode_one(self, text, prepend=None, append=None):
        # encode a single string
        # prepend/append can be either a string of a special token or a token id directly.
        check.isinstance(text, str)
        ids = []
        if prepend is not None:
            prepend_id = prepend if isinstance(prepend, int) else self.encode_special(prepend)
            ids.append(prepend_id)
        ids.extend(self.tokenizer.encode(text, add_special_tokens=False).ids)
        if append is not None:
            append_id = append if isinstance(append, int) else self.encode_special(append)
            ids.append(append_id)
        return ids

    def encode_special(self, text):
        # encode a single special token via exact match
        return self.tokenizer.token_to_id(text)

    def get_bos_token_id(self):
        bos = self.encode_special('<|bos|>')
        return bos

    def encode(self, text, *args, **kwargs):
        if isinstance(text, str):
            return self._encode_one(text, *args, **kwargs)
        elif isinstance(text, list):
            return [self._encode_one(t, *args, **kwargs) for t in text]
        else:
            raise ValueError(f'Invalid input type: {type(text)}')  # noqa

    def __call__(self, *args, **kwargs):
        return self.encode(*args, **kwargs)

    def decode(self, ids):
        return self.tokenizer.decode(ids, skip_special_tokens=False)

    def save(self, tokenizer_dir):
        # save the tokenizer to disk
        os.makedirs(tokenizer_dir, exist_ok=True)
        tokenizer_path = os.path.join(tokenizer_dir, 'tokenizer.json')
        self.tokenizer.save(tokenizer_path)
        print(f'Saved tokenizer to {tokenizer_path}')


# -----------------------------------------------------------------------------
# Tokenizer based on rustbpe + tiktoken combo


class RustBPETokenizer:
    """Light wrapper around tiktoken (for efficient inference) but train with rustbpe"""

    def __init__(self, enc, bos_token):
        self.enc = enc
        self.bos_token_id = self.encode_special(bos_token)

    @classmethod
    def train_from_iterator(cls, text_iterator, vocab_size):
        # 1) train using rustbpe
        tokenizer = rustbpe.Tokenizer()
        # the special tokens are inserted later in __init__, we don't train them here
        vocab_size_no_special = vocab_size - len(SPECIAL_TOKENS)
        check.state(vocab_size_no_special >= 256, f'vocab_size_no_special must be at least 256, got {vocab_size_no_special}')  # noqa
        tokenizer.train_from_iterator(text_iterator, vocab_size_no_special, pattern=SPLIT_PATTERN)
        # 2) construct the associated tiktoken encoding for inference
        pattern = tokenizer.get_pattern()
        mergeable_ranks_list = tokenizer.get_mergeable_ranks()
        mergeable_ranks = {bytes(k): v for k, v in mergeable_ranks_list}
        tokens_offset = len(mergeable_ranks)
        special_tokens = {name: tokens_offset + i for i, name in enumerate(SPECIAL_TOKENS)}
        enc = tiktoken.Encoding(
            name='rustbpe',
            pat_str=pattern,
            mergeable_ranks=mergeable_ranks,  # dict[bytes, int] (token bytes -> merge priority rank)
            special_tokens=special_tokens,  # dict[str, int] (special token name -> token id)
        )
        return cls(enc, '<|bos|>')

    @classmethod
    def from_directory(cls, tokenizer_dir):
        pickle_path = os.path.join(tokenizer_dir, 'tokenizer.pkl')
        with open(pickle_path, 'rb') as f:
            enc = pickle.load(f)  # noqa
        return cls(enc, '<|bos|>')

    @classmethod
    def from_pretrained(cls, tiktoken_name):
        # https://github.com/openai/tiktoken/blob/eedc8563/tiktoken_ext/openai_public.py
        enc = tiktoken.get_encoding(tiktoken_name)
        # tiktoken calls the special document delimiter token "<|endoftext|>"
        # yes this is confusing because this token is almost always PREPENDED to the beginning of the document
        # it most often is used to signal the start of a new sequence to the LLM during inference etc.
        # so in nanoChat we always use "<|bos|>" short for "beginning of sequence", but historically it is often called
        # "<|endoftext|>".
        return cls(enc, '<|endoftext|>')

    def get_vocab_size(self):
        return self.enc.n_vocab

    def get_special_tokens(self):
        return self.enc.special_tokens_set

    def id_to_token(self, id):  # noqa
        return self.enc.decode([id])

    @col.cache.cache(max_size=32)
    def encode_special(self, text):
        return self.enc.encode_single_token(text)

    def get_bos_token_id(self):
        return self.bos_token_id

    def encode(self, text, prepend=None, append=None, num_threads=8):
        # text can be either a string or a list of strings

        if prepend is not None:
            prepend_id = prepend if isinstance(prepend, int) else self.encode_special(prepend)
        if append is not None:
            append_id = append if isinstance(append, int) else self.encode_special(append)

        if isinstance(text, str):
            ids = self.enc.encode_ordinary(text)
            if prepend is not None:
                ids.insert(0, prepend_id)  # TODO: slightly inefficient here? :( hmm
            if append is not None:
                ids.append(append_id)
        elif isinstance(text, list):
            ids = self.enc.encode_ordinary_batch(text, num_threads=num_threads)
            if prepend is not None:
                for ids_row in ids:
                    ids_row.insert(0, prepend_id)  # TODO: same
            if append is not None:
                for ids_row in ids:
                    ids_row.append(append_id)
        else:
            raise ValueError(f'Invalid input type: {type(text)}')  # noqa

        return ids

    def __call__(self, *args, **kwargs):
        return self.encode(*args, **kwargs)

    def decode(self, ids):
        return self.enc.decode(ids)

    def save(self, tokenizer_dir):
        # save the encoding object to disk
        os.makedirs(tokenizer_dir, exist_ok=True)
        pickle_path = os.path.join(tokenizer_dir, 'tokenizer.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(self.enc, f)
        print(f'Saved tokenizer encoding to {pickle_path}')

    def render_conversation(self, conversation, max_tokens=2048):
        """
        Tokenize a single Chat conversation (which we call a "doc" or "document" here).
        Returns:
        - ids: list[int] is a list of token ids of this rendered conversation
        - mask: list[int] of same length, mask = 1 for tokens that the Assistant is expected to train on.
        """

        # ids, masks that we will return and a helper function to help build them up.
        ids, mask = [], []

        def add_tokens(token_ids, mask_val):
            if isinstance(token_ids, int):
                token_ids = [token_ids]
            ids.extend(token_ids)
            mask.extend([mask_val] * len(token_ids))

        # sometimes the first message is a system message...
        # => just merge it with the second (user) message
        if conversation['messages'][0]['role'] == 'system':
            # some conversation surgery is necessary here for now...
            conversation = copy.deepcopy(conversation)  # avoid mutating the original
            messages = conversation['messages']
            check.state(messages[1]['role'] == 'user', 'System message must be followed by a user message')
            messages[1]['content'] = messages[0]['content'] + '\n\n' + messages[1]['content']
            messages = messages[1:]
        else:
            messages = conversation['messages']
        check.state(len(messages) >= 1, f'Conversation has less than 1 message: {messages}')

        # fetch all the special tokens we need
        bos = self.get_bos_token_id()
        user_start, user_end = self.encode_special('<|user_start|>'), self.encode_special('<|user_end|>')
        assistant_start, assistant_end = self.encode_special('<|assistant_start|>'), self.encode_special('<|assistant_end|>')  # noqa
        python_start, python_end = self.encode_special('<|python_start|>'), self.encode_special('<|python_end|>')
        output_start, output_end = self.encode_special('<|output_start|>'), self.encode_special('<|output_end|>')

        # now we can tokenize the conversation
        add_tokens(bos, 0)
        for i, message in enumerate(messages):
            # some sanity checking here around assumptions, to prevent footguns
            must_be_from = 'user' if i % 2 == 0 else 'assistant'
            check.state(message['role'] == must_be_from, f"Message {i} is from {message['role']} but should be from {must_be_from}")  # noqa

            # content can be either a simple string or a list of parts (e.g. containing tool calls)
            content = message['content']

            if message['role'] == 'user':
                check.isinstance(content, str), 'User messages are simply expected to be strings'
                value_ids = self.encode(content)
                add_tokens(user_start, 0)
                add_tokens(value_ids, 0)
                add_tokens(user_end, 0)
            elif message['role'] == 'assistant':
                add_tokens(assistant_start, 0)
                if isinstance(content, str):
                    # simple string => simply add the tokens
                    value_ids = self.encode(content)
                    add_tokens(value_ids, 1)
                elif isinstance(content, list):
                    for part in content:
                        value_ids = self.encode(part['text'])
                        if part['type'] == 'text':
                            # string part => simply add the tokens
                            add_tokens(value_ids, 1)
                        elif part['type'] == 'python':
                            # python tool call => add the tokens inside <|python_start|> and <|python_end|>
                            add_tokens(python_start, 1)
                            add_tokens(value_ids, 1)
                            add_tokens(python_end, 1)
                        elif part['type'] == 'python_output':
                            # python output => add the tokens inside <|output_start|> and <|output_end|>
                            # none of these tokens are supervised because the tokens come from Python at test time
                            add_tokens(output_start, 0)
                            add_tokens(value_ids, 0)
                            add_tokens(output_end, 0)
                        else:
                            raise ValueError(f"Unknown part type: {part['type']}")
                else:
                    raise ValueError(f'Unknown content type: {type(content)}')
                add_tokens(assistant_end, 1)

        # truncate to max_tokens tokens MAX (helps prevent OOMs)
        ids = ids[:max_tokens]
        mask = mask[:max_tokens]
        return ids, mask

    def visualize_tokenization(self, ids, mask, with_token_id=False):
        """Small helper function useful in debugging: visualize the tokenization of render_conversation"""

        red = '\033[91m'
        green = '\033[92m'
        reset = '\033[0m'
        gray = '\033[90m'
        tokens = []
        for i, (token_id, mask_val) in enumerate(zip(ids, mask)):  # noqa
            token_str = self.decode([token_id])
            color = green if mask_val == 1 else red
            tokens.append(f'{color}{token_str}{reset}')
            if with_token_id:
                tokens.append(f'{gray}({token_id}){reset}')
        return '|'.join(tokens)

    def render_for_completion(self, conversation):
        """
        Used during Reinforcement Learning. In that setting, we want to render the conversation priming the Assistant
        for a completion. Unlike the Chat SFT case, we don't need to return the mask.
        """

        # We have some surgery to do: we need to pop the last message (of the Assistant)
        conversation = copy.deepcopy(conversation)  # avoid mutating the original
        messages = conversation['messages']
        check.state(messages[-1]['role'] == 'assistant', 'Last message must be from the Assistant')
        messages.pop()  # remove the last message (of the Assistant) inplace

        # Now tokenize the conversation
        ids, mask = self.render_conversation(conversation)

        # Finally, to prime the Assistant for a completion, append the Assistant start token
        assistant_start = self.encode_special('<|assistant_start|>')
        ids.append(assistant_start)
        return ids
