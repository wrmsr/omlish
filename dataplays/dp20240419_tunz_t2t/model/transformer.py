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
        q: Tensor,
        k: Tensor,
        mask: Tensor,
        scale: float,
) -> Tensor:
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
    sdpa = classmethod(simple_sdpa)  # noqa

    def __init__(
            self,
            hidden_size: int,
            dropout_rate: float,
            head_size: int = 8,
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
            q: Tensor,
            k: Tensor,
            v: Tensor,
            mask: Tensor,
            cache: Tensor | None = None,
    ) -> Tensor:
        orig_q_size = q.size()

        d_k = self.att_size
        d_v = self.att_size
        batch_size = q.size(0)

        # head_i = Attention(Q(W^Q)_i, K(W^K)_i, V(W^V)_i)
        q = self.linear_q(q).view(batch_size, -1, self.head_size, d_k)
        if cache is not None and 'encdec_k' in cache:
            k, v = cache['encdec_k'], cache['encdec_v']
        else:
            k = self.linear_k(k).view(batch_size, -1, self.head_size, d_k)
            v = self.linear_v(v).view(batch_size, -1, self.head_size, d_v)

            if cache is not None:
                cache['encdec_k'], cache['encdec_v'] = k, v

        q = q.transpose(1, 2)                  # [b, h, q_len, d_k]
        v = v.transpose(1, 2)                  # [b, h, v_len, d_v]
        k = k.transpose(1, 2).transpose(2, 3)  # [b, h, d_k, k_len]

        # Scaled Dot-Product Attention.
        # Attention(Q, K, V) = softmax((QK^T)/sqrt(d_k))V
        q.mul_(self.scale)
        x = torch.matmul(q, k)  # [b, h, q_len, k_len]
        x.masked_fill_(mask.unsqueeze(1).type(torch.bool), -1e9)

        x = torch.softmax(x, dim=3)

        x = self.att_dropout(x)
        x = x.matmul(v)  # [b, h, q_len, attn]

        x = x.transpose(1, 2).contiguous()  # [b, q_len, h, attn]
        x = x.view(batch_size, -1, self.head_size * d_v)

        x = self.output_layer(x)

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
            x: Tensor,
            mask: Tensor,
    ) -> Tensor:
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
            x: Tensor,
            enc_output: Tensor,
            self_mask: Tensor,
            i_mask: Tensor,
            cache: Tensor,
    ) -> Tensor:
        y = self.self_attention_norm(x)
        y = self.self_attention(y, y, y, self_mask)
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
            inputs: Tensor,
            mask: Tensor,
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
            targets: Tensor,
            enc_output: Tensor,
            i_mask: Tensor,
            t_self_mask: Tensor,
            cache: Tensor | None,
    ) -> Tensor:
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
            inputs: Tensor,
            targets: Tensor,
    ) -> Tensor:
        enc_output, i_mask = None, None
        if self.has_inputs:
            i_mask = utils.create_pad_mask(inputs, self.src_pad_idx)
            enc_output = self.encode(inputs, i_mask)

        t_mask = utils.create_pad_mask(targets, self.trg_pad_idx)
        target_size = targets.size()[1]
        t_self_mask = utils.create_trg_self_mask(target_size, device=targets.device)
        return self.decode(targets, enc_output, i_mask, t_self_mask, t_mask)

    def encode(
            self,
            inputs: Tensor,
            i_mask: Tensor,
    ) -> Tensor:
        # Input embedding
        input_embedded = self.i_vocab_embedding(inputs)
        input_embedded.masked_fill_(i_mask.squeeze(1).unsqueeze(-1), 0)
        input_embedded *= self.emb_scale
        input_embedded += self.get_position_encoding(inputs)
        input_embedded = self.i_emb_dropout(input_embedded)

        if self.fast_style_mask:
            i_mask = i_mask.size(2) - i_mask.sum(dim=2, dtype=torch.int32)
        return self.encoder(input_embedded, i_mask)

    def decode(
            self,
            targets: Tensor,
            enc_output: Tensor,
            i_mask: Tensor,
            t_self_mask: Tensor,
            t_mask: Tensor,
            cache: Tensor | None = None,
    ) -> Tensor:
        # target embedding
        target_embedded = self.t_vocab_embedding(targets)
        target_embedded.masked_fill_(t_mask.squeeze(1).unsqueeze(-1), 0)

        # Shifting
        target_embedded = target_embedded[:, :-1]
        target_embedded = F.pad(target_embedded, (0, 0, 1, 0))

        target_embedded *= self.emb_scale
        target_embedded += self.get_position_encoding(targets)
        target_embedded = self.t_emb_dropout(target_embedded)

        # decoder
        if self.fast_style_mask:
            if i_mask is not None:
                i_mask = i_mask.size(2) - i_mask.sum(dim=2, dtype=torch.int32)
            t_self_mask = t_self_mask.size(2) - t_self_mask.sum(dim=2, dtype=torch.int32)

        decoder_output = self.decoder(
            target_embedded,
            enc_output,
            i_mask,
            t_self_mask,
            cache,
        )
        # linear
        output = torch.matmul(
            decoder_output,
            self.t_vocab_embedding.weight.transpose(0, 1),
        )

        return output

    def get_position_encoding(
            self,
            x: Tensor,
    ) -> Tensor:
        max_length = x.size()[1]
        position = torch.arange(max_length, dtype=torch.float32, device=x.device)
        scaled_time = position.unsqueeze(1) * self.inv_timescales.unsqueeze(0)
        signal = torch.cat([torch.sin(scaled_time), torch.cos(scaled_time)], dim=1)
        signal = F.pad(signal, (0, 0, 0, self.hidden_size % 2))
        signal = signal.view(1, max_length, self.hidden_size)
        return signal
