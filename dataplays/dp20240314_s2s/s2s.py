"""
https://arxiv.org/pdf/1409.3215.pdf
https://github.com/nitarshan/sequence-to-sequence-learning/tree/master

python -mspacy download en_core_web_sm
python -mspacy download de_core_news_sm
"""
import collections
import itertools

from omlish import iterables

import spacy
import torch
import torch.nn as nn
import torch.nn.functional as F

# from tensorboardX import SummaryWriter
import torchtext
from torch import optim
from torch.autograd import Variable
from torch.nn.utils import clip_grad_norm
from torch.nn.utils.rnn import pack_padded_sequence
from torch.utils.data.dataloader import DataLoader
from torch.utils.data.dataset import Dataset
from torchtext import data, datasets
from torchtext.vocab import FastText


def _main():
    # Configuration
    # writer = SummaryWriter()
    use_pretrained_embeddings = False
    cuda = torch.cuda.is_available()
    print(cuda)

    def tokenizer(lang):
        return lambda text: [token.text for token in lang.tokenizer(text)]

    de_tok = spacy.load('de_core_news_sm')
    en_tok = spacy.load('en_core_web_sm')

    train, val, test = data = datasets.Multi30k()

    def gen_vocab(
            idx,
            tokenizer,
            *its,
            min_freq=10,
            specials=(),  # ('', '', '', ''),
            take: int | None = None,
    ):
        counter = collections.Counter()
        tups = (tup for it in its for tup in it)
        if take is not None:
            tups = iterables.take(take, tups)
        for tup in tups:
            counter.update(t.text for t in tokenizer(tup[idx]))
        return torchtext.vocab.vocab(counter, min_freq=min_freq, specials=specials)

    de_vocab = gen_vocab(0, de_tok, *data, take=1_000)
    en_vocab = gen_vocab(1, en_tok, *data, take=1_000)

    DE = data.Field(
        tokenize=tokenizer(de_tok),
        eos_token="<eos>",
        include_lengths=True,
        batch_first=True,
    )
    EN = data.Field(
        tokenize=tokenizer(en_tok),
        init_token="<sos>",
        eos_token="<eos>",
        include_lengths=True,
        batch_first=True,
    )

    # train, val, test = datasets.Multi30k.splits(exts=('.de', '.en'), fields=(DE, EN))
    print((len(train), len(val), len(test)))

    # Optionally use pretrained word vectors from FastText
    DE.build_vocab(train.src, vectors=FastText('de') if use_pretrained_embeddings else None)
    EN.build_vocab(train.trg, vectors=FastText('en') if use_pretrained_embeddings else None)

    de_vocab = DE.vocab
    en_vocab = EN.vocab
    print((len(de_vocab), len(en_vocab)))

    # Bi-directional 2 layer encoder, standard 4 layer decoder
    class Seq2Seq(nn.Module):
        def __init__(self, src, trg):
            super().__init__()
            SRC_EMB_SIZE = src.vectors.size(1) if use_pretrained_embeddings else 128
            TRG_EMB_SIZE = trg.vectors.size(1) if use_pretrained_embeddings else 128
            H_SIZE = 256
            LAYERS = 4

            self.src_emb = nn.Embedding(len(src), SRC_EMB_SIZE)
            self.trg_emb = nn.Embedding(len(trg), TRG_EMB_SIZE)
            if use_pretrained_embeddings:
                self.src_emb.weight = nn.Parameter(src.vectors)
                self.trg_emb.weight = nn.Parameter(trg.vectors)

            self.encoder = nn.GRU(SRC_EMB_SIZE, H_SIZE, LAYERS // 2, bidirectional=True, dropout=0.2, batch_first=True)
            self.decoder = nn.GRU(TRG_EMB_SIZE, H_SIZE, LAYERS, dropout=0.2, batch_first=True)
            self.to_trg = nn.Linear(H_SIZE, len(trg))

        def forward(self, src_sen_ids, src_lens, trg_sen_ids):
            src_sen_emb = self.src_emb(src_sen_ids)
            src_sen_emb = pack_padded_sequence(src_sen_emb, src_lens, batch_first=True)
            enc_output, enc_hidden = self.encoder(src_sen_emb)

            # Always use teacher forcing
            trg_sen_emb = self.trg_emb(trg_sen_ids)
            dec_output, dec_hidden = self.decoder(trg_sen_emb, enc_hidden)

            preds = F.log_softmax(self.to_trg(dec_output), dim=2)
            return preds

    # Model instantiation
    model = Seq2Seq(de_vocab, en_vocab)
    if cuda:
        model.cuda()
    # Masked loss function (loss from padding not computed)
    trg_mask = torch.ones(len(en_vocab))
    trg_mask[en_vocab.stoi["<pad>"]] = 0
    if cuda:
        trg_mask = trg_mask.cuda()
    criterion = nn.NLLLoss(weight=trg_mask)
    # Optimizer and learning rate scheduler
    optimizer = optim.Adam(model.parameters(), lr=5e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, 15)
    # Iterators for training and examples
    train_iter = data.BucketIterator(train, batch_size=64, sort_key=lambda ex: len(ex.src), sort_within_batch=True)
    examples = iter(data.BucketIterator(val, batch_size=1, train=False, shuffle=True, repeat=True))

    # Helper functions
    def compare_prediction(src_sen, trg_sen, pred_sen):
        print(">", ' '.join([de_vocab.itos[num] for num in src_sen.data[0]]))
        print("=", ' '.join([en_vocab.itos[num] for num in trg_sen.data[0]]))
        print("<", ' '.join([en_vocab.itos[num[0]] for num in pred_sen]))

    def batch_forward(batch):
        src_sen = batch.src[0]
        trg_sen_in = batch.trg[0][:, :-1]  # skip eos
        trg_sen = batch.trg[0][:, 1:]  # skip sos
        preds = model(src_sen, batch.src[1].cpu().numpy(), trg_sen_in)
        return src_sen, trg_sen, preds

    def sample_prediction(data_iter):
        batch = next(data_iter)
        src_sen, trg_sen, preds = batch_forward(batch)
        pred_sen = preds.topk(1)[1].data[0]
        compare_prediction(src_sen, trg_sen, pred_sen)

    # Quick sanity check
    print(sample_prediction(examples))

    for epoch in range(20):
        scheduler.step()
        # Training loop
        model.train()
        for i, batch in enumerate(train_iter):
            src_sen, trg_sen, preds = batch_forward(batch)
            loss = criterion(preds.contiguous().view(-1, preds.size(2)), trg_sen.contiguous().view(-1))
            # writer.add_scalar('data/train_loss', loss.data[0], len(train_iter) * epoch + i)
            print(f'data/train_loss, {loss.data[0]}, {len(train_iter) * epoch + i}')
            optimizer.zero_grad()
            loss.backward()
            clip_grad_norm(model.parameters(), 5.0)
            optimizer.step()
            if i == len(train_iter) - 1:
                break

        # Validation loop
        model.eval()
        val_iter = data.BucketIterator(
            val,
            batch_size=1,
            sort_key=lambda ex: len(ex.src),
            sort_within_batch=True,
            train=False,
        )
        val_loss = val_acc = 0
        for batch in val_iter:
            src_sen, trg_sen, preds = batch_forward(batch)
            val_acc += preds.topk(1)[1].data[0].view(1, -1).eq(trg_sen.data).sum() / trg_sen.size(1)
            val_loss += criterion(preds.contiguous().view(-1, preds.size(2)), trg_sen.contiguous().view(-1))
        # writer.add_scalar('data/val_loss', val_loss / len(val_iter), epoch)
        # writer.add_scalar('data/val_acc', val_acc / len(val_iter), epoch)
        print(f'data/val_loss {val_loss / len(val_iter)}, {epoch}')
        print(f'data/val_acc {val_acc / len(val_iter)}, {epoch}')

        def sample_predictions(num):
            for i in range(num):
                sample_prediction(examples)
                print()

        sample_predictions(10)


if __name__ == '__main__':
    _main()

