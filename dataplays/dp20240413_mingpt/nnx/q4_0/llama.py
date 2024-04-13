"""
https://github.com/tinygrad/tinygrad/pull/1892
"""

def convert_from_gguf(weights, params):
  def gguf_rename(tensor_name:str):
    replace_map = {"blk.": "layers.", "attn_q": "attention.wq", "attn_k": "attention.wk", "attn_v": "attention.wv", "attn_output": "attention.wo", "ffn_gate": "feed_forward.w1", "ffn_down": "feed_forward.w2", "ffn_up": "feed_forward.w3", "attn_norm": "attention_norm", "token_embd.weight": "tok_embeddings.weight", "output_norm.weight": "norm.weight"}
    for k,v in replace_map.items(): tensor_name = tensor_name.replace(k, v)
    return tensor_name
  weights = {gguf_rename(k): v for k,v in weights.items()}
  weights["rope.freqs"] = params.get('llama.rope.freq_base', 10000.)
  return weights