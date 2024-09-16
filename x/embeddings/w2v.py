"""
https://github.com/tmikolov/word2vec
https://github.com/tmikolov/word2vec/blob/20c129af10659f7c50e86e3be406df663beff438/word2vec.c
https://github.com/medallia/Word2VecJava
https://github.com/mmihaltz/word2vec-GoogleNews-vectors

https://builtin.com/machine-learning/nlp-word2vec-python

https://rare-technologies.com/parallelizing-word2vec-in-python/

https://raw.githubusercontent.com/mmihaltz/word2vec-GoogleNews-vectors/master/GoogleNews-vectors-negative300.bin.gz

https://huggingface.co/NathaNn1111/word2vec-google-news-negative-300-bin/tree/main
hf.hf_hub_download(repo_id='NathaNn1111/word2vec-google-news-negative-300-bin', filename='GoogleNews-vectors-negative300.bin')

~/.cache/huggingface/hub/models--NathaNn1111--word2vec-google-news-negative-300-bin/snapshots/78856d4586b3a938134c9833d92139f2e056e369/GoogleNews-vectors-negative300.bin

https://raw.githubusercontent.com/medallia/Word2VecJava/eb31fbb99ac6bbab82d7f807b3e2240edca50eb7/src/test/resources/com/medallia/word2vec/tokensModel.bin
https://raw.githubusercontent.com/medallia/Word2VecJava/eb31fbb99ac6bbab82d7f807b3e2240edca50eb7/src/test/resources/com/medallia/word2vec/tokensModel.txt
==

# def demo_gensim():
#     from gensim.models import word2vec
#
#     sentences = [['i', 'like', 'apple', 'pie', 'for', 'dessert'],
#                  ['i', 'dont', 'drive', 'fast', 'cars'],
#                  ['data', 'science', 'is', 'fun'],
#                  ['chocolate', 'is', 'my', 'favorite'],
#                  ['my', 'favorite', 'movie', 'is', 'predator']]
#
#     w2v = word2vec.Word2Vec(sentences, min_count=1, vector_size=5)
#
#     print(w2v)
#
#     print(w2v.wv['chocolate'])
#
#     # [-0.04609262 -0.04943436 -0.08968851 -0.08428907  0.01970964]
#
#     # list the vocabulary words
#     words = list(w2v.wv.key_to_index)
#
#     print(words)
#
#     ##
#
#     from gensim.models import KeyedVectors
#
#     w2v = KeyedVectors.load_word2vec_format(BIN_FILE, binary=True)

"""
import io
import os.path
import struct
import typing as ta

from omlish import check


BIN_FILE = os.path.join(
    os.path.expanduser('~/.cache/huggingface/hub'),
    'models--NathaNn1111--word2vec-google-news-negative-300-bin',
    'snapshots',
    '78856d4586b3a938134c9833d92139f2e056e369',
    'GoogleNews-vectors-negative300.bin',
)

TXT_FILE = os.path.join(
    os.path.expanduser('~/src'),
    'medallia/Word2VecJava',
    'src/test/resources/com/medallia/word2vec/tokensModel.txt',
)


##


def read_bin_file(
        f: ta.BinaryIO,
        *,
        max_words: int | None = None,
        max_vec_bytes: int | None = None,
) -> tuple[list[str], list[ta.Sequence[float]]]:
    buf = []
    while (c := check.not_empty(f.read(1))) != b'\n':
        buf.append(c)

    line = b''.join(buf).decode('utf-8')
    vocab_size, layer_size = map(int, line.strip().split())

    vec_fmt = '<' + 'f' * layer_size

    if max_words is not None:
        vocab_size = max(vocab_size, max_words)
    if max_vec_bytes is not None:
        vocab_size = min(vocab_size, max_vec_bytes // (layer_size * 4))

    words: list[str] = []
    vecs: list[ta.Sequence[float]] = []

    for i in range(vocab_size):
        buf = []
        while (c := check.not_empty(f.read(1))) != b' ':
            # ignore newlines in front of words (some binary files have newline, some don't)
            if c != b'\n':
                buf.append(c)
        word = b''.join(buf).decode('utf-8')
        words.append(word)

        vec_buf = f.read(4 * layer_size)
        vec = struct.unpack(vec_fmt, vec_buf)
        vecs.append(vec)

    return words, vecs


def read_txt_file(
        f: ta.TextIO,
        max_words: int | None = None,
        max_vec_bytes: int | None = None,
) -> tuple[list[str], list[ta.Sequence[float]]]:
    line = f.readline()
    vocab_size, layer_size = map(int, line.strip().split())

    if max_words is not None:
        vocab_size = max(vocab_size, max_words)
    if max_vec_bytes is not None:
        vocab_size = min(vocab_size, max_vec_bytes // (layer_size * 4))

    words: list[str] = []
    vecs: list[ta.Sequence[float]] = []

    for i in range(vocab_size):
        line = f.readline().strip().split()

        word = line[0]
        vec = list(map(float, line[1:]))

        check.equal(len(vec), layer_size)

        words.append(word)
        vecs.append(vec)

    return words, vecs


def _main():
    with open(BIN_FILE, 'rb') as f:
        words, vecs = read_bin_file(f, max_vec_bytes=0x3fffffff)

    print(len(words))

    with open(TXT_FILE) as f:
        words, vecs = read_txt_file(f, max_vec_bytes=0x3fffffff)

    print(len(words))


if __name__ == '__main__':
    _main()
