import os.path
import pprint as pp  # noqa

import numpy as np
import transformers


BASE_DIR = os.path.dirname(__file__)


def _main():
    model_name = "meta-llama/Meta-Llama-3-8B"

    if not os.path.exists(et_nd_fp := os.path.join(BASE_DIR, 'data', 'et_nd.npy')):
        pipeline = transformers.pipeline(
            "text-generation",
            model=model_name,
        )
        et_layer = pipeline.model.model.embed_tokens
        et_nd: np.ndarray = et_layer.weight.detach().cpu().numpy()
        np.save(et_nd_fp, et_nd)
    else:
        et_nd = np.load(et_nd_fp)

    # def similar_movies(movie):
    #     dists = np.dot(normalized_movies, normalized_movies[mr.movie_to_idx()[movie]])
    #     closest = np.argsort(dists)[-10:]
    #     for c in reversed(closest):
    #         print(c, mr.movies()[c].name, dists[c])
    #
    # pp.pprint(similar_movies('Rogue One'))

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_name,
        use_fast=True,
    )

    test_word = 'person'
    _, tok_id = tokenizer.encode(test_word)
    print(tok_id)

    out_word = tokenizer.decode([tok_id])
    print(out_word)


if __name__ == '__main__':
    _main()
