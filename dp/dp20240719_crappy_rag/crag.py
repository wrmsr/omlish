"""
https://github.com/HenryHengLUO/Retrieval-Augmented-Generation-Intro-Project lol
"""
import dataclasses as dc
import functools
import os.path
import re
import typing as ta

import nltk
import openai
import tiktoken
import yaml


def split_text_keep_separator(text: str, separator: str) -> list[str]:
    parts = text.split(separator)
    result = [separator + s if i > 0 else s for i, s in enumerate(parts)]
    return [s for s in result if s]


def split_by_sep(sep: str, keep_sep: bool = True) -> ta.Callable[[str], list[str]]:
    if keep_sep:
        return lambda text: split_text_keep_separator(text, sep)
    else:
        return lambda text: text.split(sep)


def split_by_sentence_tokenizer() -> ta.Callable[[str], list[str]]:
    tokenizer = nltk.tokenize.PunktSentenceTokenizer()

    def split(text: str) -> list[str]:
        spans = list(tokenizer.span_tokenize(text))
        sentences = []
        for i, span in enumerate(spans):
            start = span[0]
            if i < len(spans) - 1:
                end = spans[i + 1][0]
            else:
                end = len(text)
            sentences.append(text[start:end])

        return sentences

    return split


def split_by_regex(regex: str) -> ta.Callable[[str], list[str]]:
    return lambda text: re.findall(regex, text)


def split_by_char() -> ta.Callable[[str], list[str]]:
    return lambda text: list(text)


@dc.dataclass()
class Split:
    text: str
    is_sentence: bool


DEFAULT_PARAGRAPH_SEP = "\n\n\n"
CHUNKING_REGEX = "[^,.;。？！]+[,.;。？！]?"


def load_tiktoken_tokenizer() -> ta.Callable[[str], list]:
    # should_revert = False
    # if "TIKTOKEN_CACHE_DIR" not in os.environ:
    #     should_revert = True
    #     import llama_index
    #     os.environ["TIKTOKEN_CACHE_DIR"] = os.path.join(
    #         os.path.dirname(os.path.abspath(__file__)),
    #         "_static/tiktoken_cache",
    #     )

    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokenizer = functools.partial(enc.encode, allowed_special="all")

    # if should_revert:
    #     del os.environ["TIKTOKEN_CACHE_DIR"]

    return tokenizer


class DumbRag:
    def __init__(self) -> None:
        super().__init__()

        self.chunk_size = 64
        self.chunk_overlap = 2

        self._tokenizer = load_tiktoken_tokenizer()

        self._split_fns = [
            split_by_sep(DEFAULT_PARAGRAPH_SEP),
            split_by_sentence_tokenizer(),
        ]

        self._sub_sentence_split_fns = [
            split_by_regex(CHUNKING_REGEX),
            split_by_sep(' '),
            split_by_char(),
        ]

    def _token_size(self, text: str) -> int:
        return len(self._tokenizer(text))

    def split_text_metadata_aware(self, text: str, metadata_str: str) -> list[str]:
        metadata_len = len(self._tokenizer(metadata_str))
        effective_chunk_size = self.chunk_size - metadata_len
        if effective_chunk_size <= 0:
            raise ValueError
        return self._split_text(text, chunk_size=effective_chunk_size)

    def _get_splits_by_fns(self, text: str) -> tuple[list[str], bool]:
        for split_fn in self._split_fns:
            splits = split_fn(text)
            if len(splits) > 1:
                return splits, True

        for split_fn in self._sub_sentence_split_fns:
            splits = split_fn(text)
            if len(splits) > 1:
                break

        return splits, False

    def _split_text(self, text: str, chunk_size: int) -> list[str]:
        if text == "":
            return [text]

        splits = self._split(text, chunk_size)
        return self._merge(splits, chunk_size)

    def _split(self, text: str, chunk_size: int) -> list[Split]:
        if self._token_size(text) <= chunk_size:
            return [Split(text, is_sentence=True)]

        text_splits_by_fns, is_sentence = self._get_splits_by_fns(text)

        text_splits = []
        for text_split_by_fns in text_splits_by_fns:
            if self._token_size(text_split_by_fns) <= chunk_size:
                text_splits.append(Split(text_split_by_fns, is_sentence=is_sentence))
            else:
                recursive_text_splits = self._split(
                    text_split_by_fns,
                    chunk_size=chunk_size
                )
                text_splits.extend(recursive_text_splits)
        return text_splits

    def _merge(self, splits: list[Split], chunk_size: int) -> list[str]:
        chunks: list[str] = []
        cur_chunk: list[tuple[str, int]] = []  # list of (text, length)
        last_chunk: list[tuple[str, int]] = []
        cur_chunk_len = 0
        new_chunk = True

        def close_chunk() -> None:
            nonlocal chunks, cur_chunk, last_chunk, cur_chunk_len, new_chunk

            chunks.append("".join([text for text, length in cur_chunk]))
            last_chunk = cur_chunk
            cur_chunk = []
            cur_chunk_len = 0
            new_chunk = True

            # add overlap to the next chunk using the last one first there is a small issue with this logic. If the
            # chunk directly after the overlap is really big, then we could go over the chunk_size, and in theory the
            # correct thing to do would be to remove some/all of the overlap. However, it would complicate the logic
            # further without much real world benefit, so it's not implemented now.
            if len(last_chunk) > 0:
                last_index = len(last_chunk) - 1
                while (
                        last_index >= 0
                        and cur_chunk_len + last_chunk[last_index][1] <= self.chunk_overlap
                ):
                    text, length = last_chunk[last_index]
                    cur_chunk_len += length
                    cur_chunk.insert(0, (text, length))
                    last_index -= 1

        while len(splits) > 0:
            cur_split = splits[0]
            cur_split_len = len(self._tokenizer(cur_split.text))
            if cur_split_len > chunk_size:
                raise ValueError("Single token exceeded chunk size")
            if cur_chunk_len + cur_split_len > chunk_size and not new_chunk:
                # if adding split to current chunk exceeds chunk size: close out chunk
                close_chunk()
            else:
                if (
                        cur_split.is_sentence
                        or cur_chunk_len + cur_split_len <= chunk_size
                        or new_chunk  # new chunk, always add at least one split
                ):
                    # add split to chunk
                    cur_chunk_len += cur_split_len
                    cur_chunk.append((cur_split.text, cur_split_len))
                    splits.pop(0)
                    new_chunk = False
                else:
                    # close out chunk
                    close_chunk()

        # handle the last chunk
        if not new_chunk:
            chunk = "".join([text for text, length in cur_chunk])
            chunks.append(chunk)

        # run postprocessing to remove blank spaces
        return self._postprocess_chunks(chunks)

    def _postprocess_chunks(self, chunks: list[str]) -> list[str]:
        new_chunks = []
        for chunk in chunks:
            stripped_chunk = chunk.strip()
            if stripped_chunk == "":
                continue
            new_chunks.append(stripped_chunk)
        return new_chunks


def _main():
    with open('secrets.yml', 'r') as f:
        openai_api_key = yaml.safe_load(f)['openai_api_key']

    oai = openai.OpenAI(api_key=openai_api_key)
    del openai_api_key

    dr = DumbRag()

    docs: dict[str, str] = {}
    for fn in os.listdir(bd := os.path.join(os.path.dirname(__file__), 'docs')):
        with open(os.path.join(bd, fn)) as f:
            text = f.read()
        docs[fn] = text

        metadata_str = f'file_path: {fn}'
        splits = dr.split_text_metadata_aware(text, metadata_str)
        print(splits)

    emb_eng = 'text-embedding-ada-002'
    res = oai.embeddings.create(
        input=list(docs.values()),
        model=emb_eng,
    )
    print(res)

    query = "Who is the pretty boy in Hong Kong?"


if __name__ == '__main__':
    _main()
