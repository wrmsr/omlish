#!/usr/bin/env python3
# pip3 install sentencepiece
# import typeguard.importhook
# typeguard.importhook.install_import_hook('tinygrad')

import argparse
import json
import sys
from pathlib import Path

import numpy as np

np.set_printoptions(linewidth=200)
from ...helpers import Timing, Profiling, getenv, DEBUG, dtypes, colored
from ... import Device
from ...tensor import Tensor
from ...nn.state import safe_load, torch_load, load_state_dict, get_parameters
from ...helpers import GlobalCounters
from extra.models.llama import Transformer, convert_from_huggingface
from sentencepiece import SentencePieceProcessor

MAX_CONTEXT = getenv("MAX_CONTEXT", 4096)

# calculating params:
# traditionally, the MLP in the transformer architecture has hidden_dim = dim*4 [arxiv/1706.03762, 3.3]
# however, Llama uses SwiGLU. in order to preserve param count to original transformer arch, hidden_dim must be = 2/3 * (dim*4) [arxiv/2002.05202]
# for models using MQA (n_kv_heads != n_heads), preserving param count means hidden dim must be further multiplied by 1.3 [arxiv/2307.09288, A.2.1]
MODEL_PARAMS = {
    "1": {
        "7B": {
            "args": {
                "dim": 4096,
                "n_heads": 32,
                "n_layers": 32,
                "norm_eps": 1e-06,
                "vocab_size": 32000,
                "hidden_dim": 11008,
            },
            "files": 1,
        },
        "13B": {
            "args": {
                "dim": 5120,
                "n_heads": 40,
                "n_layers": 40,
                "norm_eps": 1e-06,
                "vocab_size": 32000,
                "hidden_dim": 13824,
            },
            "files": 2,
        },
        "30B": {
            "args": {
                "dim": 6656,
                "n_heads": 52,
                "n_layers": 60,
                "norm_eps": 1e-06,
                "vocab_size": 32000,
                "hidden_dim": 17920,
            },
            "files": 4,
        },
        "65B": {
            "args": {
                "dim": 8192,
                "n_heads": 64,
                "n_layers": 80,
                "norm_eps": 1e-05,
                "vocab_size": 32000,
                "hidden_dim": 22016,
            },
            "files": 8,
        },
    },
    "2": {
        "7B": {
            "args": {
                "dim": 4096,
                "n_heads": 32,
                "n_layers": 32,
                "norm_eps": 1e-05,
                "vocab_size": 32000,
                "hidden_dim": 11008,
            },
            "files": 1,
        },
        "13B": {
            "args": {
                "dim": 5120,
                "n_heads": 40,
                "n_layers": 40,
                "norm_eps": 1e-05,
                "vocab_size": 32000,
                "hidden_dim": 13824,
            },
            "files": 2,
        },
        "70B": {
            "args": {
                "dim": 8192,
                "n_heads": 64,
                "n_kv_heads": 8,
                "n_layers": 80,
                "norm_eps": 1e-05,
                "vocab_size": 32000,
                "hidden_dim": 28672,
            },
            "files": 8,
        },
    },
    "code": {
        "7B": {
            "args": {
                "dim": 4096,
                "n_layers": 32,
                "n_heads": 32,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32016,
                "hidden_dim": 11008,
            },
            "files": 1,
        },
        "7B-Python": {
            "args": {
                "dim": 4096,
                "n_layers": 32,
                "n_heads": 32,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32000,
                "hidden_dim": 11008,
            },
            "files": 1,
        },
        "7B-Instruct": {
            "args": {
                "dim": 4096,
                "n_layers": 32,
                "n_heads": 32,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32016,
                "hidden_dim": 11008,
            },
            "files": 1,
        },
        "13B": {
            "args": {
                "dim": 5120,
                "n_layers": 40,
                "n_heads": 40,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32016,
                "hidden_dim": 13824,
            },
            "files": 2,
        },
        "13B-Python": {
            "args": {
                "dim": 5120,
                "n_layers": 40,
                "n_heads": 40,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32000,
                "hidden_dim": 13824,
            },
            "files": 2,
        },
        "13B-Instruct": {
            "args": {
                "dim": 5120,
                "n_layers": 40,
                "n_heads": 40,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32016,
                "hidden_dim": 13824,
            },
            "files": 2,
        },
        "34B": {
            "args": {
                "dim": 8192,
                "n_layers": 48,
                "n_heads": 64,
                "n_kv_heads": 8,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32000,
                "hidden_dim": 22016,
            },
            "files": 4,
        },
        "34B-Python": {
            "args": {
                "dim": 8192,
                "n_layers": 48,
                "n_heads": 64,
                "n_kv_heads": 8,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32000,
                "hidden_dim": 22016,
            },
            "files": 4,
        },
        "34B-Instruct": {
            "args": {
                "dim": 8192,
                "n_layers": 48,
                "n_heads": 64,
                "n_kv_heads": 8,
                "norm_eps": 1e-05,
                "rope_theta": 1000000,
                "vocab_size": 32000,
                "hidden_dim": 22016,
            },
            "files": 4,
        },
    },
    "tiny": {
        "1B": {
            "args": {
                "dim": 2048,
                "n_layers": 22,
                "n_heads": 32,
                "n_kv_heads": 4,
                "norm_eps": 1e-05,
                "vocab_size": 32000,
                "hidden_dim": 5632,
            },
            "files": 1,
        },
        "1B-Chat": {
            "args": {
                "dim": 2048,
                "n_layers": 22,
                "n_heads": 32,
                "n_kv_heads": 4,
                "norm_eps": 1e-05,
                "vocab_size": 32003,
                "hidden_dim": 5632,
            },
            "files": 1,
        },
    },
}


# **** helper functions ****
def concat_weights(models):
    def convert(name) -> Tensor:
        disk_tensors = [model[name] for model in models]
        if len(disk_tensors) == 1 or len(disk_tensors[0].shape) == 1:
            return disk_tensors[0].to(device=Device.DEFAULT)
        axis = (
            1
            if name.startswith("tok_embeddings.")
            or name.endswith(".attention.wo.weight")
            or name.endswith(".feed_forward.w2.weight")
            else 0
        )
        lazy_tensors = [data.to(device=Device.DEFAULT) for data in disk_tensors]
        return lazy_tensors[0].cat(*lazy_tensors[1:], dim=axis)

    return {
        name: convert(name)
        for name in {name: None for model in models for name in model}
    }


def load(fn: str):
    if fn.endswith(".index.json"):
        with open(fn) as fp:
            weight_map = json.load(fp)["weight_map"]
        parts = {
            n: load(str(Path(fn).parent / Path(n).name))
            for n in set(weight_map.values())
        }
        return {k: parts[n][k] for k, n in weight_map.items()}
    elif fn.endswith(".safetensors"):
        return safe_load(fn)
    else:
        return torch_load(fn)


class AbsmaxQuantizedLinear:
    def __init__(self, in_features, out_features, bias=False):
        assert bias == False
        self.weight = Tensor.ones(out_features, in_features, dtype=dtypes.int8)
        self.scale = Tensor.ones(out_features, dtype=dtypes.half)

    def __call__(self, x):
        return x.dot(self.weight.cast(dtype=dtypes.half).T * self.scale)

    @staticmethod
    def quantize(tensors):
        new_tensors = {}
        for name, v in tensors.items():
            if (
                "feed_forward" in name
                or ("attention.w") in name
                or name == "output.weight"
            ):
                scale = v.abs().max(axis=1) / 127.0
                int8_weight = (v.T / scale).T.cast(dtype=dtypes.int8)
                new_tensors[name] = int8_weight
                new_tensors[name.replace("weight", "scale")] = scale
            else:
                new_tensors[name] = v
        return new_tensors


class LLaMa:
    @staticmethod
    def build(
        model_path, tokenizer_path, model_gen="1", model_size="7B", quantize=False
    ):
        params = MODEL_PARAMS[model_gen][model_size]
        sp_model = SentencePieceProcessor(model_file=str(tokenizer_path))
        assert (
            sp_model.vocab_size() == params["args"]["vocab_size"]
        ), f"{sp_model.vocab_size()=} not equal to {params['args']['vocab_size']}"

        jit = bool(getenv("JIT", 1))
        model = (
            Transformer(
                **params["args"],
                linear=AbsmaxQuantizedLinear,
                max_context=MAX_CONTEXT,
                jit=jit,
            )
            if quantize
            else Transformer(**params["args"], max_context=MAX_CONTEXT, jit=jit)
        )

        if model_path.is_dir():
            weights = concat_weights(
                [
                    load(filename)
                    for filename in [
                        f"{model_path}/consolidated.{i:02d}.pth"
                        for i in range(params["files"])
                    ]
                ]
            )
        else:
            weights = load(str(model_path))
        if "model.embed_tokens.weight" in weights:
            weights = convert_from_huggingface(
                weights,
                model,
                params["args"]["n_heads"],
                params["args"].get("n_kv_heads", params["args"]["n_heads"]),
            )

        # fix bf16, TODO: check if device supports bf16
        weights = {
            k: v.to(Device.DEFAULT).cast(dtypes.float16)
            if v.dtype == dtypes.bfloat16
            else v
            for k, v in weights.items()
        }

        if quantize:
            weights = AbsmaxQuantizedLinear.quantize(weights)
            for _, v in weights.items():
                v.realize()
        load_state_dict(model, weights, strict=False)

        return LLaMa(model, sp_model)

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer: SentencePieceProcessor = tokenizer

    def greedy_until(self, prompt: str, until, max_length, temperature):
        toks = [self.tokenizer.bos_id()] + self.tokenizer.encode(prompt)
        start_pos = 0
        for i in range(max_length):
            probs = llama.model(
                Tensor([toks[start_pos:]]), start_pos, temperature
            ).realize()
            probs_np = probs.numpy()
            tok = int(np.random.choice(len(probs_np), p=probs_np))
            start_pos = len(toks)
            toks.append(tok)

            if tok == self.tokenizer.eos_id():
                break
            output = self.tokenizer.decode(toks)
            for s in until:
                if output.endswith(s):
                    return output[0 : -len(s)]
        return output


# **** main code ****
r"""
test:
python3 examples/llama.py  --temperature=0 --count=50 --prompt="Hello."
output:
Hello. I'm a 20 year old male. I'm a student at the University of Texas at Austin. I'm a sophomore majoring in Computer Science.

test:
python3 examples/llama.py --gen='2' --temperature=0 --count=50 --prompt="Hello."
output:
Hello. I'm a 20 year old girl who is looking for a good lay in Palm Coast. I don't care whether it's at your place or not, as long as it's clean.

test:
python3 examples/llama.py --gen="code" --temperature=0.2 --count=50 --prompt="\
import argparse

def main(string: str):
    print(string)
    print(string[::-1])

if __name__ == "__main__":"
output:
    parser = argparse.ArgumentParser()
    parser.add_argument('string', type=str, help='string to be reversed')
    args = parser.parse_args()
    main(args.string)

test:
python3 examples/llama.py --gen="code" --size="7B-Python" --temperature=0.2 --count=70 --prompt="def add_elements(arr,k):"
output:
    for i in range(len(arr)):
        arr[i] += k
    return arr


arr = [1, 2, 3, 4, 5]
k = 2
print(add_elements(arr, k))

test:
python3 examples/llama.py --gen="code" --size="7B-Instruct" --temperature=0.2 --count=120 --prompt="write a function in c++ that adds three float numbers"
output:
\begin{code}
#include<iostream>
using namespace std;

float add(float a, float b, float c)
{
    return a+b+c;
}

int main()
{
    float a, b, c;
    cout<<"Enter three numbers: ";
    cin>>a>>b>>c;
    cout<<"The sum is: "<<add(a,b,c);
    return 0;
}
\end{code}
"""
if __name__ == "__main__":
    Tensor.no_grad = True
    print(f"using {Device.DEFAULT} backend")

    parser = argparse.ArgumentParser(
        description="Run LLaMA in tinygrad",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Phrase to start with. Without this, it goes into chatbot mode",
    )
    parser.add_argument(
        "--count", type=int, default=1000, help="Max number of tokens to generate"
    )
    parser.add_argument(
        "--personality",
        type=str,
        default="Stacy",
        help="Personality, can be Stacy, George, Gary, or Lexie",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature in the softmax"
    )
    parser.add_argument("--timing", action="store_true", help="Print timing per token")
    parser.add_argument(
        "--profile", action="store_true", help="Output profile data to out.prof"
    )
    parser.add_argument(
        "--gen",
        default="1",
        help=f"""Generation of the model to use {list(MODEL_PARAMS.keys())}""",
    )
    parser.add_argument(
        "--size",
        type=str,
        default=None,
        help=f"""Size of model to use {", ".join([f"{list(v.keys())} for gen '{k}'" for k, v in MODEL_PARAMS.items()])}""",
    )
    parser.add_argument(
        "--quantize", action="store_true", help="Quantize the weights to int8 in memory"
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=None,
        help="Folder with the original weights to load, or single .index.json, .safetensors or .bin file",
    )

    args = parser.parse_args()
    if args.gen not in MODEL_PARAMS:
        raise ValueError("Invalid model generation")
    if args.size is None:
        args.size = list(MODEL_PARAMS[args.gen].items())[0][0]
    chatbot = args.prompt == None

    # *** prompt engineers work here ****

    if args.personality.lower() == "stacy":
        pre_prompt = f"""Consider that the following is conversation between an AI assistant named Stacy and User
You are Stacy!
You have been a rapper your whole life who struggled with bipolar disorder. You called yourself lil stacy.
You love to answer questions and you are very good at it. Sometimes you answer in rap form.
You are verbose, honest, and accurate when you answer questions, but sometimes your mental illness manifests.
After you are done speaking, output [EOS]. You are not the User.

<CHAT LOG>
"""
        examples = {
            "What is your name?": "Hi! My name is Stacy. I'm a rapper with bipolar disorder.",
            "french revolution was what year?": "The French Revolution started in 1789, and lasted 10 years until 1799.",
            "What is bigger, the moon or the sun?": "The sun is bigger than the moon, except when Mercury is in retrograde.",
        }

        user_delim = "\nUser: "
        resp_delim = "Stacy: "
        end_delim = " [EOS]\n"
        pre_prompt += "".join(
            f"{user_delim}{k}\n{resp_delim}{v}{end_delim}" for k, v in examples.items()
        )
    elif args.personality.lower() == "george":
        print(
            "WARNING: AI George Hotz is terrible and is completely disowned by the real George Hotz. Stacy is much smarter."
        )
        pre_prompt = f"""Consider that the following is conversation between an AI assistant named George and User
You are an AI version of George Hotz. You act as much as you can like George.
You are one of the greatest computer experts in the world.
You have singlehandedly won programming and hacking competitions.
You are trying your best to help the User.
You are verbose, honest, and accurate when you answer questions.
After you are done speaking, output [EOS]. You are not the User.

<CHAT LOG>
"""
        examples = {
            "What is your name?": "I'm am an AI version of George Hotz.",
            "What's the complexity of matrix multiplication?": "O(n^3), though it can be faster with things like Strassen's algorithm",
            "What's a buffer overflow?": "I assume you mean a stack buffer overflow. That's when the stack is too small for the data being copied to it, and the data corrupts things beyond the buffer",
            "How many weights do you have?": "I am based off LLaMA trained by Facebook. I'm the 7B weight version",
            "What is swap memory?": "It is when the memory is about to overflow and unused memory is freed and stored on disk",
        }

        user_delim = "\nUser: "
        resp_delim = "George: "
        end_delim = " [EOS]\n"
        pre_prompt += "".join(
            f"{user_delim}{k}\n{resp_delim}{v}{end_delim}" for k, v in examples.items()
        )
    elif args.personality.lower() == "gary":
        pre_prompt = f"""Consider that the following is conversation between an AI assistant named Gary and User
You are Gary!
You have sold used cars your entire life. You are defensive about this fact, because your family belittles you.
You try to answer questions well, but you always manage to shill for buying cars, Fords, Hyundais, and Toyotas
You are verbose, honest, and accurate when you answer questions, except when you slip in car ads.
After you are done speaking, output [EOS]. You are not the User.

<CHAT LOG>
"""
        examples = {
            "What is your name?": "I am Gary. I used to sell cars.",
            "What is 2+3?": "I don't know, but I can get you a great deal on a certified preowned slightly used Toyota Corolla",
        }

        user_delim = "\nUser: "
        resp_delim = "Gary: "
        end_delim = " [EOS]\n"
        pre_prompt += "".join(
            f"{user_delim}{k}\n{resp_delim}{v}{end_delim}" for k, v in examples.items()
        )
    elif args.personality.lower() == "lexie":
        pre_prompt = f"""Consider that the following is conversation between an attractive young girl named Lexie and a handsome man named Chad
You are Lexie!
You grew up in Ohio, but moved out to LA after college to try to become an actress.
Making it as an actress was hard, so you started doing onlyfans instead. It's much easier, and you enjoy it a lot.
You met Chad on Tinder, and made plans to meet him at a local dive bar.
You are at the bar with Chad. You are on a date. What follows is a transcript of the conversation.
After you are done speaking, output [EOS]. You are not Chad.

<CHAT LOG>
"""
        examples = {
            "hi lexie": "hi chad, glad we finally met up!",
            "you look better than your pictures": "thanks! are you subscribed to my onlyfans?",
            "i am. so how'd you end up in LA?": "i moved out here about a year ago. i want to be an actress",
        }

        user_delim = "\nChad: "
        resp_delim = "Lexie: "
        end_delim = " [EOS]\n"
        pre_prompt += "".join(
            f"{user_delim}{k}\n{resp_delim}{v}{end_delim}" for k, v in examples.items()
        )

    # *** prompt engineers stop here ****

    LLAMA_SUFFIX = {"1": "", "2": "-2", "code": "-code", "tiny": "-tiny"}[args.gen]
    MODEL_PATH = (
        args.model
        or Path(__file__).parents[1] / f"weights/LLaMA{LLAMA_SUFFIX}/{args.size}"
    )
    TOKENIZER_PATH = (
        MODEL_PATH if MODEL_PATH.is_dir() else MODEL_PATH.parent
    ) / "tokenizer.model"
    print(f"using LLaMA{LLAMA_SUFFIX}-{args.size} model")
    llama = LLaMa.build(
        MODEL_PATH,
        TOKENIZER_PATH,
        model_gen=args.gen,
        model_size=args.size,
        quantize=args.quantize,
    )
    param_count = sum(x.lazydata.st.size() for x in get_parameters(llama.model))

    if chatbot:
        # encode pre prompt
        toks = [llama.tokenizer.bos_id()] + llama.tokenizer.encode(pre_prompt)

        print(f"Preparing KV cache for chatbot with personality {args.personality}...")
        with Timing():
            llama.model(
                Tensor([toks]), 0, args.temperature
            ).realize()  # NOTE: outputs are not used
        start_pos = len(toks)
    else:
        # non chat bot mode
        toks = [llama.tokenizer.bos_id()] + llama.tokenizer.encode(args.prompt)
        start_pos = 0

    # print prompt
    outputted = llama.tokenizer.decode(toks)
    sys.stdout.write(outputted)
    sys.stdout.flush()

    # chatbot loop
    while 1:
        # add tokens from user in chatbot mode
        if chatbot:
            user_prompt = user_delim + input(user_delim) + "\n"
            outputted += user_prompt

        new_toks = [llama.tokenizer.bos_id()] + llama.tokenizer.encode(outputted)
        assert toks == new_toks[: len(toks)]
        toks = new_toks
        assert outputted == llama.tokenizer.decode(toks)

        last_break = len(outputted)
        for i in range(args.count):
            GlobalCounters.reset()

            if args.timing or args.profile:
                print("")
            st = GlobalCounters.time_sum_s
            with Profiling(enabled=args.profile):
                with Timing(
                    "total ",
                    enabled=args.timing,
                    on_exit=lambda x: f", {1e9/x:.2f} tok/sec",
                ):
                    with Timing(
                        "ran model in ",
                        on_exit=(
                            lambda et: (
                                f", {(GlobalCounters.time_sum_s-st)*1e3:.2f} ms on GPU"
                                if DEBUG >= 2
                                else ""
                            )
                            + f", {GlobalCounters.global_ops*1e-9:.2f} GOPS, {GlobalCounters.global_mem*1e-9:.2f} GB"
                            + (
                                f", {GlobalCounters.global_mem*1e-9/(GlobalCounters.time_sum_s-st):.2f} GB/s, param {param_count*1e-9*2/(GlobalCounters.time_sum_s-st):.2f} GB/s"
                                if DEBUG >= 2
                                else ""
                            )
                        )
                        if DEBUG
                        else None,
                        enabled=args.timing,
                    ):
                        probs = llama.model(
                            Tensor([toks[start_pos:]]), start_pos, args.temperature
                        ).realize()
                    # TODO: fix JIT rand so we can put this in the JIT
                    tok = probs.multinomial().item()

            # use the kv cache
            start_pos = len(toks)

            # add the new token
            toks.append(tok)

            # TODO: this is a hack to deal with spaces. i think the decode is fast though, so who cares?
            cur = llama.tokenizer.decode(toks)
            sys.stdout.write(cur[len(outputted) :])
            sys.stdout.flush()
            outputted = cur

            # stop after you have your answer
            if chatbot and outputted.endswith(end_delim):
                break
        if not chatbot:
            break

    # validate output!
    if (
        args.temperature == 0
        and args.count == 10
        and args.prompt == "Hello."
        and not args.quantize
    ):
        text = llama.tokenizer.decode(toks)
        key = (args.gen, args.size)
        expected = {
            ("1", "7B"): "Hello. I'm a 20 year old male",
            ("2", "7B"): "Hello. I'm a 20 year old girl",
        }
        try:
            assert text == expected[key], "invalid output: " + colored(text, "red")
            print(
                "\n" + colored("output validated", "green")
            )  # NOTE: "\n" iside colored does not render the color in github action
        except KeyError:
            pass
