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

    # et_lengths = np.linalg.norm(et_nd, axis=1)
    # normalized_ets = (et_lengths.T / et_lengths).T
    normalized_ets = et_nd

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_name,
        use_fast=True,
    )

    test_word = 'person'
    _, tok_id = tokenizer.encode(test_word)
    print(tok_id)

    dists = np.dot(normalized_ets, normalized_ets[tok_id])
    closest = np.argsort(dists)[-100:]
    for c in reversed(closest):
        out_word = tokenizer.decode([c])
        print(out_word)


if __name__ == '__main__':
    _main()
