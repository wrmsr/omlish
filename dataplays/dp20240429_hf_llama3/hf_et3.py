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

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_name,
        use_fast=True,
    )

    test_word = 'horse'
    n = 100

    _, tok_id = tokenizer.encode(test_word)
    print((float('inf'), tok_id, test_word))

    dists = np.dot(et_nd, et_nd[tok_id])
    closest = np.argsort(dists)[::-1]
    if closest[0] != tok_id:
        raise ValueError((tok_id, closest[0]))
    for c in closest[1:1 + n]:
        out_word = tokenizer.decode([c])
        print((dists[c], c, out_word))


if __name__ == '__main__':
    _main()
