"""
https://neptune.ai/blog/how-to-code-bert-using-pytorch-tutorial

https://colab.research.google.com/drive/13FjI_uXaw8JJGjzjVX3qKSLyW9p3b6OV?usp=sharing#scrollTo=s1PGksqBNuZM

This code is possible because of [Tae-Hwan Jung](https://github.com/graykode). I have just broken down the code and
added few things here and here for better understanding.
"""
import dataclasses as dc
import functools
import math
import random
import re
import typing as ta

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


@dc.dataclass(frozen=True)
class Config:
    maxlen = 30  # maximum of length
    batch_size = 6
    max_pred = 5  # max tokens of prediction
    n_layers = 6  # number of Encoder layers
    n_heads = 12  # number of heads in Multi-Head Attention
    d_model = 768  # Embedding Size
    d_ff = 768 * 4  # 4*d_model, FeedForward dimension
    d_k = d_v = 64  # dimension of K(=Q), V
    n_segments = 2


@dc.dataclass(frozen=True)
class Corpus:
    sentences: ta.Sequence[str]
    token_list: ta.Sequence[ta.Sequence[int]]
    word_dict: ta.Mapping[str, int]
    vocab_size: int
    number_dict: ta.Mapping[int, str]


def build_corpus(text: str) -> Corpus:
    sentences = re.sub("[.,!?\\-]", '', text.lower()).split('\n')  # filter '.', ',', '?', '!'
    word_list = list(set(" ".join(sentences).split()))
    word_dict = {'[PAD]': 0, '[CLS]': 1, '[SEP]': 2, '[MASK]': 3}

    for i, w in enumerate(word_list):
        word_dict[w] = i + 4
    number_dict = {i: w for i, w in enumerate(word_dict)}
    vocab_size = len(word_dict)

    token_list = list()
    for sentence in sentences:
        arr = [word_dict[s] for s in sentence.split()]
        token_list.append(arr)

    return Corpus(
        sentences=sentences,
        token_list=token_list,
        word_dict=word_dict,
        vocab_size=vocab_size,
        number_dict=number_dict,
    )


def make_batch(
        config: Config,
        corpus: Corpus,
) -> list[list[list[int]]]:
    batch = []
    positive = negative = 0
    while positive != config.batch_size / 2 or negative != config.batch_size / 2:
        tokens_a_index, tokens_b_index = random.randrange(len(corpus.sentences)), random.randrange(len(corpus.sentences))
        tokens_a, tokens_b = corpus.token_list[tokens_a_index], corpus.token_list[tokens_b_index]

        input_ids = [corpus.word_dict['[CLS]'], *tokens_a, corpus.word_dict['[SEP]'],  *tokens_b, corpus.word_dict['[SEP]']]

        segment_ids = [0] * (1 + len(tokens_a) + 1) + [1] * (len(tokens_b) + 1)

        # MASK LM
        n_pred = min(config.max_pred, max(1, int(round(len(input_ids) * 0.15))))  # 15 % of tokens in one sentence

        cand_maked_pos = [
            i
            for i, token in enumerate(input_ids)
            if token != corpus.word_dict['[CLS]'] and token != corpus.word_dict['[SEP]']
        ]
        random.shuffle(cand_maked_pos)
        masked_tokens, masked_pos = [], []
        for pos in cand_maked_pos[:n_pred]:
            masked_pos.append(pos)
            masked_tokens.append(input_ids[pos])
            if random.random() < 0.8:  # 80%
                input_ids[pos] = corpus.word_dict['[MASK]']  # make mask
            elif random.random() < 0.5:  # 10%
                index = random.randint(0, corpus.vocab_size - 1)  # random index in vocabulary
                input_ids[pos] = corpus.word_dict[corpus.number_dict[index]]  # replace

        # Zero Paddings
        n_pad = config.maxlen - len(input_ids)
        input_ids.extend([0] * n_pad)
        segment_ids.extend([0] * n_pad)

        # Zero Padding (100% - 15%) tokens
        if config.max_pred > n_pred:
            n_pad = config.max_pred - n_pred
            masked_tokens.extend([0] * n_pad)
            masked_pos.extend([0] * n_pad)

        if tokens_a_index + 1 == tokens_b_index and positive < config.batch_size / 2:
            batch.append([input_ids, segment_ids, masked_tokens, masked_pos, True])  # IsNext
            positive += 1
        elif tokens_a_index + 1 != tokens_b_index and negative < config.batch_size / 2:
            batch.append([input_ids, segment_ids, masked_tokens, masked_pos, False])  # NotNext
            negative += 1

    return batch


def get_attn_pad_mask(
        seq_q: torch.Tensor,  # (bs, max_len)
        seq_k: torch.Tensor,  # (bs, max_len)
) -> torch.Tensor:  # (bs, max_len, max_len)
    batch_size, len_q = seq_q.size()
    batch_size, len_k = seq_k.size()
    # eq(zero) is PAD token
    pad_attn_mask = seq_k.data.eq(0).unsqueeze(1)  # batch_size x 1 x len_k(=len_q), one is masking
    return pad_attn_mask.expand(batch_size, len_q, len_k)  # batch_size x len_q x len_k


def gelu(x: torch.tensor) -> torch.Tensor:
    return x * 0.5 * (1.0 + torch.erf(x / math.sqrt(2.0)))


class Embedding(nn.Module):
    def __init__(self, config: Config, vocab_size: int) -> None:
        super().__init__()
        self.tok_embed = nn.Embedding(vocab_size, config.d_model)  # token embedding
        self.pos_embed = nn.Embedding(config.maxlen, config.d_model)  # position embedding
        self.seg_embed = nn.Embedding(config.n_segments, config.d_model)  # segment(token type) embedding
        self.norm = nn.LayerNorm(config.d_model)

    def forward(
            self,
            x: torch.Tensor,  # (bs, max_len)
            seg: torch.Tensor,  # (bs, max_len)
    ) -> torch.Tensor:  # (bs, max_len, d_model)
        seq_len = x.size(1)
        pos = torch.arange(seq_len, dtype=torch.long)
        pos = pos.unsqueeze(0).expand_as(x)  # (seq_len,) -> (batch_size, seq_len)
        embedding = self.tok_embed(x) + self.pos_embed(pos) + self.seg_embed(seg)
        return self.norm(embedding)


class ScaledDotProductAttention(nn.Module):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config

    def forward(
            self,
            q: torch.Tensor,
            k: torch.Tensor,
            v: torch.Tensor,
            attn_mask: torch.Tensor,
    ) -> tuple[
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
    ]:
        scores = torch.matmul(q, k.transpose(-1, -2)) / np.sqrt(self.config.d_k)  # (batch_size x n_heads x len_q(=len_k) x len_k(=len_q))  # noqa
        scores.masked_fill_(attn_mask, -1e9)  # Fills elements of self tensor with value where mask is one.
        attn = nn.Softmax(dim=-1)(scores)
        context = torch.matmul(attn, v)
        return scores, context, attn


class MultiHeadAttention(nn.Module):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.w_q = nn.Linear(config.d_model, config.d_k * config.n_heads)
        self.w_k = nn.Linear(config.d_model, config.d_k * config.n_heads)
        self.w_v = nn.Linear(config.d_model, config.d_v * config.n_heads)

    def forward(
            self,
            q: torch.Tensor,  # (batch_size x len_q x d_model)
            k: torch.Tensor,  # (batch_size x len_k x d_model)
            v: torch.Tensor,  # (batch_size x len_k x d_model)
            attn_mask: torch.Tensor,
    ) -> tuple[
         torch.Tensor,
         torch.Tensor,
     ]:
        residual, batch_size = q, q.size(0)

        # (B, S, D) -proj-> (B, S, D) -split-> (B, S, H, W) -trans-> (B, H, S, W)
        q_s = self.w_q(q).view(batch_size, -1, self.config.n_heads, self.config.d_k).transpose(1, 2)  # (batch_size x n_heads x len_q x d_k)  # noqa
        k_s = self.w_k(k).view(batch_size, -1, self.config.n_heads, self.config.d_k).transpose(1, 2)  # (batch_size x n_heads x len_k x d_k)  # noqa
        v_s = self.w_v(v).view(batch_size, -1, self.config.n_heads, self.config.d_v).transpose(1, 2)  # (batch_size x n_heads x len_k x d_v)  # noqa

        attn_mask = attn_mask.unsqueeze(1).repeat(1, self.config.n_heads, 1, 1)  # (batch_size x n_heads x len_q x len_k)

        (
            _,
            context,  # (batch_size x n_heads x len_q x d_v)
            attn,  # (batch_size x n_heads x len_q(=len_k) x len_k(=len_q))
        ) = ScaledDotProductAttention(self.config)(q_s, k_s, v_s, attn_mask)

        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.config.n_heads * self.config.d_v)  # (batch_size x len_q x n_heads * d_v)  # noqa
        output = nn.Linear(self.config.n_heads * self.config.d_v, self.config.d_model)(context)
        return nn.LayerNorm(self.config.d_model)(output + residual), attn  # (batch_size x len_q x d_model)


class PoswiseFeedForwardNet(nn.Module):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.fc1 = nn.Linear(config.d_model, config.d_ff)
        self.fc2 = nn.Linear(config.d_ff, config.d_model)

    def forward(
            self,
            x: torch.Tensor,
    ) -> torch.Tensor:
        # (batch_size, len_seq, d_model) -> (batch_size, len_seq, d_ff) -> (batch_size, len_seq, d_model)
        return self.fc2(gelu(self.fc1(x)))


class EncoderLayer(nn.Module):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.enc_self_attn = MultiHeadAttention(config)
        self.pos_ffn = PoswiseFeedForwardNet(config)

    def forward(
            self,
            enc_inputs: torch.Tensor,
            enc_self_attn_mask: torch.Tensor,
    ) -> tuple[
        torch.Tensor,
        torch.Tensor,
    ]:
        enc_outputs, attn = self.enc_self_attn(
            enc_inputs,  # enc_inputs to same Q,K,V
            enc_inputs,
            enc_inputs,
            enc_self_attn_mask,
        )
        enc_outputs = self.pos_ffn(enc_outputs)  # enc_outputs: [batch_size x len_q x d_model]
        return enc_outputs, attn


class BERT(nn.Module):
    def __init__(self, config: Config, vocab_size: int) -> None:
        super().__init__()
        self.embedding = Embedding(config, vocab_size)
        self.layers = nn.ModuleList([EncoderLayer(config) for _ in range(config.n_layers)])
        self.fc = nn.Linear(config.d_model, config.d_model)
        self.activ1 = nn.Tanh()
        self.linear = nn.Linear(config.d_model, config.d_model)
        self.activ2 = gelu
        self.norm = nn.LayerNorm(config.d_model)
        self.classifier = nn.Linear(config.d_model, 2)
        # decoder is shared with embedding layer
        embed_weight = self.embedding.tok_embed.weight
        n_vocab, n_dim = embed_weight.size()
        self.decoder = nn.Linear(n_dim, n_vocab, bias=False)
        self.decoder.weight = embed_weight
        self.decoder_bias = nn.Parameter(torch.zeros(n_vocab))

    def forward(
            self,
            input_ids: torch.Tensor,
            segment_ids: torch.Tensor,
            masked_pos: torch.Tensor,
    ) -> tuple[
        torch.Tensor,
        torch.Tensor,
    ]:
        output = self.embedding(input_ids, segment_ids)
        enc_self_attn_mask = get_attn_pad_mask(input_ids, input_ids)
        for layer in self.layers:
            (
                output,  # (batch_size, len, d_model)
                enc_self_attn,  # (batch_size, n_heads, d_mode, d_model)
            ) = layer(output, enc_self_attn_mask)

        # it will be decided by first token(CLS)
        h_pooled = self.activ1(self.fc(output[:, 0]))  # (batch_size, d_model)
        logits_clsf = self.classifier(h_pooled)  # (batch_size, 2)

        masked_pos = masked_pos[:, :, None].expand(-1, -1, output.size(-1))  # (batch_size, max_pred, d_model)

        # get masked position from final output of transformer.
        h_masked = torch.gather(output, 1, masked_pos)  # masking position (batch_size, max_pred, d_model)
        h_masked = self.norm(self.activ2(self.linear(h_masked)))

        logits_lm = self.decoder(h_masked) + self.decoder_bias  # (batch_size, max_pred, n_vocab)

        return logits_lm, logits_clsf


def _main() -> None:
    config = Config()

    ##

    text = (
        'Hello, how are you? I am Romeo.\n'
        'Hello, Romeo My name is Juliet. Nice to meet you.\n'
        'Nice meet you too. How are you today?\n'
        'Great. My baseball team won the competition.\n'
        'Oh Congratulations, Juliet\n'
        'Thanks you Romeo'
    )

    corpus = build_corpus(text)

    print(corpus.token_list)

    ##

    do_make_batch = functools.partial(
        make_batch,
        config,
        corpus,
    )

    batch = do_make_batch()

    input_ids, segment_ids, masked_tokens, masked_pos, isNext = map(torch.LongTensor, zip(*batch))

    print(get_attn_pad_mask(input_ids, input_ids)[0][0], input_ids[0])

    ##

    emb = Embedding(config, corpus.vocab_size)
    embeds = emb(input_ids, segment_ids)

    attenM = get_attn_pad_mask(input_ids, input_ids)

    SDPA = ScaledDotProductAttention(config)(embeds, embeds, embeds, attenM)

    S, C, A = SDPA

    # print('Masks', masks[0][0])
    print()
    print('Scores: ', S[0][0], '\n\nAttention M: ', A[0][0])

    ##

    emb = Embedding(config, corpus.vocab_size)
    embeds = emb(input_ids, segment_ids)

    attenM = get_attn_pad_mask(input_ids, input_ids)

    MHA = MultiHeadAttention(config)(embeds, embeds, embeds, attenM)

    Output, A = MHA

    print(A[0][0])

    ##

    model = BERT(config, corpus.vocab_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    batch = do_make_batch()
    input_ids, segment_ids, masked_tokens, masked_pos, isNext = map(torch.LongTensor, zip(*batch))

    for epoch in range(10):
        optimizer.zero_grad()
        logits_lm, logits_clsf = model(input_ids, segment_ids, masked_pos)
        loss_lm = criterion(logits_lm.transpose(1, 2), masked_tokens)  # for masked LM
        loss_lm = (loss_lm.float()).mean()
        loss_clsf = criterion(logits_clsf, isNext)  # for sentence classification
        loss = loss_lm + loss_clsf
        if (epoch + 1) % 10 == 0:
            print('Epoch:', '%04d' % (epoch + 1), 'cost =', '{:.6f}'.format(loss))
        loss.backward()
        optimizer.step()

    # Predict mask tokens ans isNext
    input_ids, segment_ids, masked_tokens, masked_pos, isNext = map(torch.LongTensor, zip(batch[0]))
    print(text)
    print([corpus.number_dict[w.item()] for w in input_ids[0] if corpus.number_dict[w.item()] != '[PAD]'])

    logits_lm, logits_clsf = model(input_ids, segment_ids, masked_pos)
    logits_lm = logits_lm.data.max(2)[1][0].data.numpy()
    print('masked tokens list : ', [pos.item() for pos in masked_tokens[0] if pos.item() != 0])
    print('predict masked tokens list : ', [pos for pos in logits_lm if pos != 0])

    logits_clsf = logits_clsf.data.max(1)[1].data.numpy()[0]
    print('isNext : ', True if isNext else False)
    print('predict isNext : ', True if logits_clsf else False)


if __name__ == '__main__':
    _main()

