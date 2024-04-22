import math

from torch import Tensor
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..utils import utils
from .common import FeedForwardNetwork
from .common import initialize_weight


# pylint: disable=arguments-differ


def simple_sdpa(
        q: Tensor,  # (bs, head_size, seq_len, att_size)
        k: Tensor,  # (bs, head_size, att_size, seq_len)
        mask: Tensor,  # (bs, 1, seq_len)
        scale: float,
) -> Tensor:  # (bs, head_size, seq_len, seq_len)
    # Scaled Dot-Product Attention.
    # Attention(Q, K, V) = softmax((QK^T)/sqrt(d_k))V
    q.mul_(scale)
    x = torch.matmul(q, k)  # [b, h, q_len, k_len]
    x.masked_fill_(mask.unsqueeze(1).type(torch.bool), -1e9)
    return x


def fast_sdpa(q, k, mask, scale):
    # from tcop.masked_softmax import MaskedSoftmax
    # https://github.com/tunz/tcop-pytorch/blob/fe5dada36964085850d5a50405498c193fb5c426/tcop/masked_softmax.py
    # -> git+https://github.com/wrmsr/tcop-pytorch/tree/deb0a2deb4ef998d89c33c2f1d618df64bb206a4
    x = torch.matmul(q, k)  # [b, h, q_len, k_len]
    x = MaskedSoftmax.apply(x, mask, scale)  # noqa
    return x


class MultiHeadAttention(nn.Module):
    sdpa = staticmethod(simple_sdpa)

    def __init__(
            self,
            hidden_size: int,
            dropout_rate: float,
            head_size: int = 8,  # num_heads, really
    ) -> None:
        super().__init__()

        self.head_size = head_size

        self.att_size = att_size = hidden_size // head_size
        self.scale = att_size ** -0.5

        self.linear_q = nn.Linear(hidden_size, head_size * att_size, bias=False)
        self.linear_k = nn.Linear(hidden_size, head_size * att_size, bias=False)
        self.linear_v = nn.Linear(hidden_size, head_size * att_size, bias=False)
        initialize_weight(self.linear_q)
        initialize_weight(self.linear_k)
        initialize_weight(self.linear_v)

        self.att_dropout = nn.Dropout(dropout_rate)

        self.output_layer = nn.Linear(head_size * att_size, hidden_size, bias=False)
        initialize_weight(self.output_layer)

    def forward(
            self,
            q: Tensor,  # (bs, seq_len, hidden_size)
            k: Tensor,  # (bs, seq_len, hidden_size)
            v: Tensor,  # (bs, seq_len, hidden_size)
            mask: Tensor,  # (1, seq_len, seq_len)
            cache: Tensor | None = None,
    ) -> Tensor:  # (bs, seq_len, hidden_size)
        orig_q_size = q.size()

        d_k = self.att_size
        d_v = self.att_size
        batch_size = q.size(0)

        # head_i = Attention(Q(W^Q)_i, K(W^K)_i, V(W^V)_i)
        q = self.linear_q(q).view(batch_size, -1, self.head_size, d_k)  # (bs, seq_len, head_size, att_size)
        if cache is not None and 'encdec_k' in cache:
            k, v = cache['encdec_k'], cache['encdec_v']
        else:
            k = self.linear_k(k).view(batch_size, -1, self.head_size, d_k)  # (bs, seq_len, head_size, att_size)
            v = self.linear_v(v).view(batch_size, -1, self.head_size, d_v)  # (bs, seq_len, head_size, att_size)
            # (bs, seq_len, head_size, att_size)
            if cache is not None:
                cache['encdec_k'], cache['encdec_v'] = k, v

        q = q.transpose(1, 2)                  # [b, h, q_len, d_k]  # (bs, head_size, seq_len, att_size)
        v = v.transpose(1, 2)                  # [b, h, v_len, d_v]  # (bs, head_size, seq_len, att_size)
        k = k.transpose(1, 2).transpose(2, 3)  # [b, h, d_k, k_len]  # (bs, head_size, att_size, seq_len)

        x = self.sdpa(q, k, mask, self.scale)

        x = torch.softmax(x, dim=3)

        x = self.att_dropout(x)
        x = x.matmul(v)  # [b, h, q_len, attn]  # (bs, head_size, seq_len, att_size)

        x = x.transpose(1, 2).contiguous()  # [b, q_len, h, attn]  # (bs, seq_len, head_size, att_size)
        x = x.view(batch_size, -1, self.head_size * d_v)  # (bs, seq_len, hidden_size)

        x = self.output_layer(x)  # (bs, seq_len, hidden_size)

        assert x.size() == orig_q_size
        return x


class EncoderLayer(nn.Module):
    def __init__(
            self,
            hidden_size: int,
            filter_size: int,
            dropout_rate: float,
    ) -> None:
        super().__init__()

        self.self_attention_norm = nn.LayerNorm(hidden_size, eps=1e-6)
        self.self_attention = MultiHeadAttention(hidden_size, dropout_rate)
        self.self_attention_dropout = nn.Dropout(dropout_rate)

        self.ffn_norm = nn.LayerNorm(hidden_size, eps=1e-6)
        self.ffn = FeedForwardNetwork(hidden_size, filter_size, dropout_rate)
        self.ffn_dropout = nn.Dropout(dropout_rate)

    def forward(
            self,
            x: Tensor,  # (bs, seq_len, hidden_size)
            mask: Tensor,  # (bs, 1, seq_len)
    ) -> Tensor:  # (bs, seq_len, hidden_size)
        y = self.self_attention_norm(x)
        y = self.self_attention(y, y, y, mask)
        y = self.self_attention_dropout(y)
        x = x + y

        y = self.ffn_norm(x)
        y = self.ffn(y)
        y = self.ffn_dropout(y)
        x = x + y
        return x


class DecoderLayer(nn.Module):
    def __init__(
            self,
            hidden_size: int,
            filter_size: int,
            dropout_rate: float,
    ) -> None:
        super().__init__()

        self.self_attention_norm = nn.LayerNorm(hidden_size, eps=1e-6)
        self.self_attention = MultiHeadAttention(hidden_size, dropout_rate)
        self.self_attention_dropout = nn.Dropout(dropout_rate)

        self.enc_dec_attention_norm = nn.LayerNorm(hidden_size, eps=1e-6)
        self.enc_dec_attention = MultiHeadAttention(hidden_size, dropout_rate)
        self.enc_dec_attention_dropout = nn.Dropout(dropout_rate)

        self.ffn_norm = nn.LayerNorm(hidden_size, eps=1e-6)
        self.ffn = FeedForwardNetwork(hidden_size, filter_size, dropout_rate)
        self.ffn_dropout = nn.Dropout(dropout_rate)

    def forward(
            self,
            x: Tensor,  # (bs, seq_len, hidden_size)
            enc_output: Tensor,  # (bs, seq_len, hidden_size)
            self_mask: Tensor,  # (1, seq_len, seq_len)
            i_mask: Tensor,  # (bs, 1, seq_len)
            cache: Tensor | None,
    ) -> Tensor:  # (bs, seq_len, hidden_size)
        y = self.self_attention_norm(x)  # (bs, seq_len, hidden_size)
        y = self.self_attention(y, y, y, self_mask)  # (bs, seq_len, hidden_size)
        y = self.self_attention_dropout(y)
        x = x + y

        if enc_output is not None:
            y = self.enc_dec_attention_norm(x)
            y = self.enc_dec_attention(y, enc_output, enc_output, i_mask, cache)
            y = self.enc_dec_attention_dropout(y)
            x = x + y

        y = self.ffn_norm(x)
        y = self.ffn(y)
        y = self.ffn_dropout(y)
        x = x + y
        return x


class Encoder(nn.Module):
    def __init__(
            self,
            hidden_size: int,
            filter_size: int,
            dropout_rate: float,
            n_layers: int,
    ) -> None:
        super().__init__()

        encoders = [
            EncoderLayer(hidden_size, filter_size, dropout_rate)
            for _ in range(n_layers)
        ]
        self.layers = nn.ModuleList(encoders)

        self.last_norm = nn.LayerNorm(hidden_size, eps=1e-6)

    def forward(
            self,
            inputs: Tensor,  # (bs, seq_len, hidden_size)
            mask: Tensor,  # (bs, 1, seq_len)
    ) -> Tensor:
        encoder_output = inputs
        for enc_layer in self.layers:
            encoder_output = enc_layer(encoder_output, mask)
        return self.last_norm(encoder_output)


class Decoder(nn.Module):
    def __init__(
            self,
            hidden_size: int,
            filter_size: int,
            dropout_rate: float,
            n_layers: int,
    ) -> None:
        super().__init__()

        decoders = [
            DecoderLayer(hidden_size, filter_size, dropout_rate)
            for _ in range(n_layers)
        ]
        self.layers = nn.ModuleList(decoders)

        self.last_norm = nn.LayerNorm(hidden_size, eps=1e-6)

    def forward(
            self,
            targets: Tensor,  # (bs, seq_len, hidden_size)
            enc_output: Tensor,  # (bs, seq_len, hidden_size)
            i_mask: Tensor,  # (bs, 1, seq_len)
            t_self_mask: Tensor,  # (1, seq_len, seq_len)
            cache: Tensor | None,
    ) -> Tensor:  # (bs, seq_len, hidden_size)
        decoder_output = targets
        for i, dec_layer in enumerate(self.layers):
            layer_cache = None
            if cache is not None:
                if i not in cache:
                    cache[i] = {}
                layer_cache = cache[i]
            decoder_output = dec_layer(
                decoder_output,
                enc_output,
                t_self_mask,
                i_mask,
                layer_cache,
            )
        return self.last_norm(decoder_output)


class Transformer(nn.Module):
    fast_style_mask = False

    def __init__(
            self,
            i_vocab_size: int,
            t_vocab_size: int,
            n_layers: int = 6,
            hidden_size: int = 512,
            filter_size: int = 2048,
            dropout_rate: float = 0.1,
            share_target_embedding: bool = True,
            has_inputs: bool = True,
            src_pad_idx=None,
            trg_pad_idx=None,
    ):
        super().__init__()

        self.hidden_size = hidden_size
        self.emb_scale = hidden_size ** 0.5
        self.has_inputs = has_inputs
        self.src_pad_idx = src_pad_idx
        self.trg_pad_idx = trg_pad_idx

        self.t_vocab_embedding = nn.Embedding(t_vocab_size, hidden_size)
        nn.init.normal_(
            self.t_vocab_embedding.weight,
            mean=0,
            std=hidden_size**-0.5,
        )
        self.t_emb_dropout = nn.Dropout(dropout_rate)
        self.decoder = Decoder(
            hidden_size,
            filter_size,
            dropout_rate,
            n_layers,
        )

        if has_inputs:
            if not share_target_embedding:
                self.i_vocab_embedding = nn.Embedding(i_vocab_size, hidden_size)
                nn.init.normal_(self.i_vocab_embedding.weight, mean=0, std=hidden_size**-0.5)
            else:
                self.i_vocab_embedding = self.t_vocab_embedding

            self.i_emb_dropout = nn.Dropout(dropout_rate)

            self.encoder = Encoder(
                hidden_size,
                filter_size,
                dropout_rate,
                n_layers,
            )

        # For positional encoding
        num_timescales = self.hidden_size // 2
        max_timescale = 10000.0
        min_timescale = 1.0
        log_timescale_increment = (
            math.log(float(max_timescale) / float(min_timescale)) /
            max(num_timescales - 1, 1)
        )
        inv_timescales = min_timescale * torch.exp(
            torch.arange(num_timescales, dtype=torch.float32) *
            -log_timescale_increment,
        )
        self.register_buffer('inv_timescales', inv_timescales)

    def forward(
            self,
            inputs: Tensor,  # (bs, seq_len)
            targets: Tensor,  # (bs, seq_len)
    ) -> Tensor:  # (bs, seq_len, num_tok)
        enc_output, i_mask = None, None
        if self.has_inputs:
            i_mask = utils.create_pad_mask(inputs, self.src_pad_idx)
            enc_output = self.encode(inputs, i_mask)  # (bs, seq_len, hidden_size)

        t_mask = utils.create_pad_mask(targets, self.trg_pad_idx)  # (bs, 1, seq_len)
        target_size = targets.size()[1]
        t_self_mask = utils.create_trg_self_mask(target_size, device=targets.device)  # (1, seq_len, seq_len)
        return self.decode(targets, enc_output, i_mask, t_self_mask, t_mask)

    def encode(
            self,
            inputs: Tensor,  # (bs, seq_len)
            i_mask: Tensor,  # (bs, 1, seq_len)
    ) -> Tensor:  # (bs, seq_len, hidden_size)
        # Input embedding
        input_embedded = self.i_vocab_embedding(inputs)  # (bs, seq_len, hidden_size)
        input_embedded.masked_fill_(i_mask.squeeze(1).unsqueeze(-1), 0)
        input_embedded *= self.emb_scale
        input_embedded += self.get_position_encoding(inputs)
        input_embedded = self.i_emb_dropout(input_embedded)

        if self.fast_style_mask:
            i_mask = i_mask.size(2) - i_mask.sum(dim=2, dtype=torch.int32)
        return self.encoder(input_embedded, i_mask)

    def decode(
            self,
            targets: Tensor,  # (bs, seq_len)
            enc_output: Tensor,  # (bs, seq_len, hidden_size)
            i_mask: Tensor,  # bs, 1, seq_len)
            t_self_mask: Tensor,  # (1, seq_len, seq_len)
            t_mask: Tensor,  # (bs, 1, seq_len)
            cache: Tensor | None = None,
    ) -> Tensor:  # (bs, seq_len, num_tok)
        # target embedding
        target_embedded = self.t_vocab_embedding(targets)  # (bs, seq_len, hidden_size)
        target_embedded.masked_fill_(t_mask.squeeze(1).unsqueeze(-1), 0)

        # Shifting
        target_embedded = target_embedded[:, :-1]  # (bs, seq_len - 1, hidden_size)
        target_embedded = F.pad(target_embedded, (0, 0, 1, 0))  # (bs, seq_len, hidden_size)

        target_embedded *= self.emb_scale
        target_embedded += self.get_position_encoding(targets)
        target_embedded = self.t_emb_dropout(target_embedded)

        # decoder
        if self.fast_style_mask:
            if i_mask is not None:
                i_mask = i_mask.size(2) - i_mask.sum(dim=2, dtype=torch.int32)
            t_self_mask = t_self_mask.size(2) - t_self_mask.sum(dim=2, dtype=torch.int32)

        decoder_output = self.decoder(  # (bs, seq_len, hidden_size)
            target_embedded,
            enc_output,
            i_mask,
            t_self_mask,
            cache,
        )
        # linear
        output = torch.matmul(  # (bs, seq_len, num_tok)
            decoder_output,
            self.t_vocab_embedding.weight.transpose(0, 1),
        )

        return output

    def get_position_encoding(
            self,
            x: Tensor,  # (bs, seq_len)
    ) -> Tensor:  # (1, seq_len, hidden_size)
        max_length = x.size()[1]
        position = torch.arange(max_length, dtype=torch.float32, device=x.device)
        scaled_time = position.unsqueeze(1) * self.inv_timescales.unsqueeze(0)
        signal = torch.cat([torch.sin(scaled_time), torch.cos(scaled_time)], dim=1)
        signal = F.pad(signal, (0, 0, 0, self.hidden_size % 2))
        signal = signal.view(1, max_length, self.hidden_size)
        return signal
