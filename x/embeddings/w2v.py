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
"""
import os.path


BIN_FILE = os.path.join(
    os.path.expanduser('~/.cache/huggingface/hub'),
    'models--NathaNn1111--word2vec-google-news-negative-300-bin',
    'snapshots',
    '78856d4586b3a938134c9833d92139f2e056e369',
    'GoogleNews-vectors-negative300.bin',
)


def _main():
    from gensim.models import word2vec

    sentences = [['i', 'like', 'apple', 'pie', 'for', 'dessert'],
                 ['i', 'dont', 'drive', 'fast', 'cars'],
                 ['data', 'science', 'is', 'fun'],
                 ['chocolate', 'is', 'my', 'favorite'],
                 ['my', 'favorite', 'movie', 'is', 'predator']]

    w2v = word2vec.Word2Vec(sentences, min_count=1, vector_size=5)

    print(w2v)

    print(w2v.wv['chocolate'])

    # [-0.04609262 -0.04943436 -0.08968851 -0.08428907  0.01970964]

    # list the vocabulary words
    words = list(w2v.wv.key_to_index)

    print(words)

    ##

    from gensim.models import KeyedVectors

    w2v = KeyedVectors.load_word2vec_format(BIN_FILE, binary=True)


if __name__ == '__main__':
    _main()
