"""
**Author**: `Sean Robertson <https://github.com/spro>`_
"""
import abc
import io
import math
import os.path
import pickle
import random
import re
import time
import typing as ta
import unicodedata

from omlish import lang

if ta.TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as matplotlib_ticker
else:
    plt = lang.proxy_import('matplotlib.pyplot')
    matplotlib_ticker = lang.proxy_import('matplotlib.ticker')

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim
import torch.utils.data


Pair: ta.TypeAlias = tuple[str, str]
Tensor: ta.TypeAlias = torch.Tensor


BASE_DIR = os.path.dirname(__file__)


## Data


class Lang:
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0: "SOS", 1: "EOS"}
        self.n_words = 2  # Count SOS and EOS

    def add_sentence(self, sentence: str) -> None:
        for word in sentence.split(' '):
            self.add_word(word)

    def add_word(self, word: str) -> None:
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1


# Turn a Unicode string to plain ASCII, thanks to
# https://stackoverflow.com/a/518232/2809427
def unicode_to_ascii(s: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


# Lowercase, trim, and remove non-letter characters
def normalize_string(s: str) -> str:
    s = unicode_to_ascii(s.lower().strip())
    s = re.sub(r"([.!?])", r" \1", s)
    s = re.sub(r"[^a-zA-Z!?]+", r" ", s)
    return s.strip()


def read_langs(lang1: str, lang2: str, reverse: bool = False) -> tuple[Lang, Lang, list[Pair]]:
    # Read the file and split into lines
    with io.open('data/%s-%s.txt' % (lang1, lang2), encoding='utf-8') as f:
        lines = f.read().strip().split('\n')

    # Split every line into pairs and normalize
    pairs = ta.cast(list[Pair], [tuple(normalize_string(s) for s in l.split('\t')) for l in lines])

    # Reverse pairs, make Lang instances
    if reverse:
        pairs = [p[::-1] for p in pairs]
        input_lang = Lang(lang2)
        output_lang = Lang(lang1)
    else:
        input_lang = Lang(lang1)
        output_lang = Lang(lang2)

    return input_lang, output_lang, pairs


MAX_LENGTH = 10

eng_prefixes = (
    "i am ", "i m ",
    "he is", "he s ",
    "she is", "she s ",
    "you are", "you re ",
    "we are", "we re ",
    "they are", "they re "
)


def filter_pair(p: Pair) -> bool:
    return len(p[0].split(' ')) < MAX_LENGTH and \
        len(p[1].split(' ')) < MAX_LENGTH and \
        p[1].startswith(eng_prefixes)


def filter_pairs(pairs: ta.Iterable[Pair]) -> list[Pair]:
    return [pair for pair in pairs if filter_pair(pair)]


def prepare_data(lang1: str, lang2: str, reverse: bool = False) -> tuple[Lang, Lang, list[Pair]]:
    pkl_file_path = os.path.join(BASE_DIR, f'i_s2s_xlat2_data_{lang1}_{lang2}{"_rev" if reverse else ""}.pkl')
    if os.path.exists(pkl_file_path):
        with open(pkl_file_path, 'rb') as f:
            return pickle.load(f)

    input_lang, output_lang, pairs = read_langs(lang1, lang2, reverse)

    pairs = filter_pairs(pairs)

    for pair in pairs:
        input_lang.add_sentence(pair[0])
        output_lang.add_sentence(pair[1])

    tup = input_lang, output_lang, pairs

    with open(pkl_file_path, 'wb') as f:
        pickle.dump(tup, f)

    return tup


## Models


SOS_token = 0
EOS_token = 1


class EncoderRNN(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, dropout_p: float = 0.1) -> None:
        super().__init__()
        self.hidden_size = hidden_size

        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.dropout = nn.Dropout(dropout_p)

    def __call__(self, input: Tensor) -> tuple[Tensor, Tensor]:  # output, hidden
        return super().__call__(input)

    def forward(self, input: Tensor) -> tuple[Tensor, Tensor]:  # output, hidden
        embedded = self.dropout(self.embedding(input))
        output, hidden = self.gru(embedded)
        return output, hidden


class DecoderRNN(abc.ABC):
    @abc.abstractmethod
    def __call__(
            self,
            encoder_outputs: Tensor,
            encoder_hidden: Tensor,
            target_tensor: Tensor | None = None,
    ) -> tuple[Tensor, Tensor, Tensor | None]:  # outputs, hidden, None
        raise NotImplemented


class DumbDecoderRNN(nn.Module, DecoderRNN):
    def __init__(self, hidden_size: int, output_size: int) -> None:
        super().__init__()
        self.embedding = nn.Embedding(output_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.out = nn.Linear(hidden_size, output_size)

    def forward(
            self,
            encoder_outputs: Tensor,
            encoder_hidden: Tensor,
            target_tensor: Tensor | None = None,
    ) -> tuple[Tensor, Tensor, Tensor | None]:  # outputs, hidden, None
        batch_size = encoder_outputs.size(0)
        decoder_input = torch.empty(batch_size, 1, dtype=torch.long, device=encoder_hidden.device).fill_(SOS_token)
        decoder_hidden = encoder_hidden
        decoder_outputs = []

        for i in range(MAX_LENGTH):
            decoder_output, decoder_hidden = self.forward_step(decoder_input, decoder_hidden)
            decoder_outputs.append(decoder_output)

            if target_tensor is not None:
                # Teacher forcing: Feed the target as the next input
                decoder_input = target_tensor[:, i].unsqueeze(1)  # Teacher forcing
            else:
                # Without teacher forcing: use its own predictions as the next input
                _, topi = decoder_output.topk(1)
                decoder_input = topi.squeeze(-1).detach()  # detach from history as input

        decoder_outputs = torch.cat(decoder_outputs, dim=1)
        decoder_outputs = F.log_softmax(decoder_outputs, dim=-1)
        return decoder_outputs, decoder_hidden, None  # We return `None` for consistency in the training loop

    def forward_step(self, input: Tensor, hidden: Tensor) -> tuple[Tensor, Tensor]:
        output = self.embedding(input)
        output = F.relu(output)
        output, hidden = self.gru(output, hidden)
        output = self.out(output)
        return output, hidden


class BahdanauAttention(nn.Module):
    def __init__(self, hidden_size: int) -> None:
        super().__init__()
        self.Wa = nn.Linear(hidden_size, hidden_size)  # query
        self.Ua = nn.Linear(hidden_size, hidden_size)  # keys
        self.Va = nn.Linear(hidden_size, 1)

    def forward(
            self,
            query: Tensor,  # (B, 1, 128)
            keys: Tensor,  # (B, 10, 128)
    ) -> tuple[Tensor, Tensor]:
        scores = self.Va(torch.tanh(self.Wa(query) + self.Ua(keys)))  # (B, 10, 1)
        scores = scores.squeeze(2).unsqueeze(1)  # (B, 1, 10)

        weights = F.softmax(scores, dim=-1)  # (B, 1, 10)
        context = torch.bmm(weights, keys)  # (B, 1, 128)

        return context, weights


class AttnDecoderRNN(nn.Module, DecoderRNN):
    def __init__(self, hidden_size: int, output_size: int, dropout_p: float = 0.1) -> None:
        super().__init__()
        self.embedding = nn.Embedding(output_size, hidden_size)
        self.attention = BahdanauAttention(hidden_size)
        self.gru = nn.GRU(2 * hidden_size, hidden_size, batch_first=True)
        self.out = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout_p)

    def forward(
            self,
            encoder_outputs: Tensor,  # (B, 10, 128)
            encoder_hidden: Tensor,  # (1, B, 128)
            target_tensor: Tensor | None = None,
    ) -> tuple[
        Tensor,  # output: (B, 10, 2991)
        Tensor,  # hidden: (1, B, 128)
        Tensor,  # attention: (B, 10, 10)
    ]:
        batch_size = encoder_outputs.size(0)
        decoder_input = torch.empty(batch_size, 1, dtype=torch.long, device=encoder_hidden.device).fill_(SOS_token)
        decoder_hidden = encoder_hidden
        decoder_outputs = []
        attentions = []

        for i in range(MAX_LENGTH):
            decoder_output, decoder_hidden, attn_weights = self.forward_step(
                decoder_input, decoder_hidden, encoder_outputs
            )
            decoder_outputs.append(decoder_output)
            attentions.append(attn_weights)

            if target_tensor is not None:
                # Teacher forcing: Feed the target as the next input
                decoder_input = target_tensor[:, i].unsqueeze(1)  # Teacher forcing
            else:
                # Without teacher forcing: use its own predictions as the next input
                _, topi = decoder_output.topk(1)
                decoder_input = topi.squeeze(-1).detach()  # detach from history as input

        decoder_outputs = torch.cat(decoder_outputs, dim=1)
        decoder_outputs = F.log_softmax(decoder_outputs, dim=-1)
        attentions = torch.cat(attentions, dim=1)

        return decoder_outputs, decoder_hidden, attentions

    def forward_step(
            self,
            input: Tensor,  # (B, 1)
            hidden: Tensor,  # (1, B, 128)
            encoder_outputs: Tensor,  # (B, 10, 128)
    ) -> tuple[
        Tensor,  # output: (B, 1, 2991)
        Tensor,  # hidden: (1, B, 128)
        Tensor,  # attn_weights: (B, 1, 10)
    ]:
        embedded = self.dropout(self.embedding(input))  # (B, 1, 128)

        query = hidden.permute(1, 0, 2)  # (B, 1, 128)
        context, attn_weights = self.attention(query, encoder_outputs)  # (B, 1, 128), (B, 1, 10)
        input_gru = torch.cat((embedded, context), dim=2)  # (B, 1, 256)

        output, hidden = self.gru(input_gru, hidden)  # (B, 1, 128), (1, B, 128)
        output = self.out(output)  # (B, 1, 2991)

        return output, hidden, attn_weights


## Execution


def indexes_from_sentence(lang: Lang, sentence: str) -> list[int]:
    return [lang.word2index[word] for word in sentence.split(' ')]


def tensor_from_sentence(lang: Lang, sentence: str, device: torch.device) -> Tensor:
    indexes = indexes_from_sentence(lang, sentence)
    indexes.append(EOS_token)
    return torch.tensor(indexes, dtype=torch.long, device=device).view(1, -1)


def build_dataloader(
        input_lang: Lang,
        output_lang: Lang,
        pairs: ta.Sequence[Pair],
        batch_size: int,
        device: torch.device,
) -> torch.utils.data.DataLoader:
    n = len(pairs)
    input_ids = np.zeros((n, MAX_LENGTH), dtype=np.int32)
    target_ids = np.zeros((n, MAX_LENGTH), dtype=np.int32)

    for idx, (inp, tgt) in enumerate(pairs):
        inp_ids = indexes_from_sentence(input_lang, inp)
        tgt_ids = indexes_from_sentence(output_lang, tgt)
        inp_ids.append(EOS_token)
        tgt_ids.append(EOS_token)
        input_ids[idx, :len(inp_ids)] = inp_ids
        target_ids[idx, :len(tgt_ids)] = tgt_ids

    train_data = torch.utils.data.TensorDataset(
        torch.LongTensor(input_ids).to(device),
        torch.LongTensor(target_ids).to(device)
    )

    train_sampler = torch.utils.data.RandomSampler(train_data)
    train_dataloader = torch.utils.data.DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)
    return train_dataloader


def train_epoch(
        dataloader: torch.utils.data.DataLoader,
        encoder: EncoderRNN,
        decoder: DecoderRNN,
        encoder_optimizer: torch.optim.Optimizer,
        decoder_optimizer: torch.optim.Optimizer,
        criterion: ta.Callable[..., Tensor],
):
    total_loss = 0
    for data in dataloader:
        input_tensor, target_tensor = data

        encoder_optimizer.zero_grad()
        decoder_optimizer.zero_grad()

        encoder_outputs, encoder_hidden = encoder(input_tensor)
        decoder_outputs, _, _ = decoder(encoder_outputs, encoder_hidden, target_tensor)

        loss = criterion(
            decoder_outputs.view(-1, decoder_outputs.size(-1)),
            target_tensor.view(-1)
        )
        loss.backward()

        encoder_optimizer.step()
        decoder_optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)


def format_minutes(s: float) -> str:
    m = math.floor(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)


def format_time_since(since: float, percent: float) -> str:
    now = time.time()
    s = now - since
    es = s / (percent)
    rs = es - s
    return '%s (- %s)' % (format_minutes(s), format_minutes(rs))


def train(
        train_dataloader: torch.utils.data.DataLoader,
        encoder: EncoderRNN,
        decoder: DecoderRNN,
        n_epochs: int,
        learning_rate: float = 0.001,
        print_every: int = 100,
        plot_every: int = 100,
) -> None:
    start = time.time()
    plot_losses = []
    print_loss_total = 0  # Reset every print_every
    plot_loss_total = 0  # Reset every plot_every

    encoder_optimizer = torch.optim.Adam(encoder.parameters(), lr=learning_rate)
    decoder_optimizer = torch.optim.Adam(decoder.parameters(), lr=learning_rate)
    criterion = nn.NLLLoss()

    for epoch in range(1, n_epochs + 1):
        loss = train_epoch(
            train_dataloader,
            encoder,
            decoder,
            encoder_optimizer,
            decoder_optimizer,
            criterion,
        )
        print_loss_total += loss
        plot_loss_total += loss

        if epoch % print_every == 0:
            print_loss_avg = print_loss_total / print_every
            print_loss_total = 0
            print('%s (%d %d%%) %.4f' % (
                format_time_since(start, epoch / n_epochs),
                epoch,
                epoch / n_epochs * 100,
                print_loss_avg,
            ))

        if epoch % plot_every == 0:
            plot_loss_avg = plot_loss_total / plot_every
            plot_losses.append(plot_loss_avg)
            plot_loss_total = 0


def evaluate(
        encoder: EncoderRNN,
        decoder: DecoderRNN,
        sentence: str,
        input_lang: Lang,
        output_lang: Lang,
        device: torch.device,
) -> tuple[list[str], Tensor | None]:
    with torch.no_grad():
        input_tensor = tensor_from_sentence(input_lang, sentence, device)

        encoder_outputs, encoder_hidden = encoder(input_tensor)
        decoder_outputs, decoder_hidden, decoder_attn = decoder(encoder_outputs, encoder_hidden)

        _, topi = decoder_outputs.topk(1)
        decoded_ids = topi.squeeze()

        decoded_words = []
        for idx in decoded_ids:
            if idx.item() == EOS_token:
                decoded_words.append('<EOS>')
                break
            decoded_words.append(output_lang.index2word[idx.item()])

    return decoded_words, decoder_attn


def evaluate_randomly(
        input_lang: Lang,
        output_lang: Lang,
        pairs: ta.Sequence[Pair],
        encoder: EncoderRNN,
        decoder: DecoderRNN,
        device: torch.device,
        n: int = 10,
) -> None:
    for i in range(n):
        pair = random.choice(pairs)
        print('>', pair[0])
        print('=', pair[1])

        output_words, _ = evaluate(
            encoder,
            decoder,
            pair[0],
            input_lang,
            output_lang,
            device,
        )

        output_sentence = ' '.join(output_words)
        print('<', output_sentence)
        print('')


def show_attention(
        input_sentence: str,
        output_words: list[str],
        attentions: torch.tensor,
) -> None:
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(attentions.cpu().numpy(), cmap='bone')
    fig.colorbar(cax)

    # Set up axes
    ax.set_xticklabels([''] + input_sentence.split(' ') + ['<EOS>'], rotation=90)
    ax.set_yticklabels([''] + output_words)

    # Show label at every tick
    ax.xaxis.set_major_locator(matplotlib_ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(matplotlib_ticker.MultipleLocator(1))

    plt.show()


def evaluate_and_show_attention(
        input_lang: Lang,
        output_lang: Lang,
        encoder: EncoderRNN,
        decoder: DecoderRNN,
        input_sentence: str,
        device: torch.device,
) -> None:
    output_words, attentions = evaluate(
        encoder,
        decoder,
        input_sentence,
        input_lang,
        output_lang,
        device,
    )

    print('input =', input_sentence)
    print('output =', ' '.join(output_words))

    if PLOT and attentions is not None:
        show_attention(
            input_sentence,
            output_words,
            attentions[0, :len(output_words), :],
        )


PLOT = True


def _main() -> None:
    if PLOT:
        plt.ion()  # interactive mode

    hidden_size = 128
    batch_size = 32

    input_lang, output_lang, pairs = prepare_data('eng', 'fra', True)

    device = torch.device("cuda" if torch.cuda.is_available() else "mps")

    train_dataloader = build_dataloader(input_lang, output_lang, pairs, batch_size, device)

    encoder = EncoderRNN(input_lang.n_words, hidden_size).to(device)

    use_attn: bool = True
    load_files: bool = False
    save_files: bool = False

    if use_attn:
        decoder = AttnDecoderRNN(hidden_size, output_lang.n_words).to(device)
    else:
        decoder = DumbDecoderRNN(hidden_size, output_lang.n_words).to(device)

    file_suff = 'attn' if use_attn else 'dumb'
    enc_file_path = os.path.join(BASE_DIR, f'i_s2s_xlat_{file_suff}_enc.pth')
    dec_file_path = os.path.join(BASE_DIR, f'i_s2s_xlat_{file_suff}_dec.pth')

    # if PLOT:
    #     plt.switch_backend('agg')

    if load_files and os.path.exists(enc_file_path):
        assert os.path.exists(dec_file_path)

        encoder.load_state_dict(torch.load(enc_file_path, map_location=device))
        decoder.load_state_dict(torch.load(dec_file_path, map_location=device))

    else:
        train(train_dataloader, encoder, decoder, 80, print_every=5, plot_every=5)

        if save_files:
            torch.save(encoder.state_dict(), enc_file_path)
            torch.save(decoder.state_dict(), dec_file_path)

    encoder.eval()
    decoder.eval()

    # evaluate_randomly(input_lang, output_lang, pairs, encoder, decoder, device)

    for s in [
        'il n est pas aussi grand que son pere',
        'je suis trop fatigue pour conduire',
        'je suis desole si c est une question idiote',
        'je suis reellement fiere de vous',
    ]:
        evaluate_and_show_attention(input_lang, output_lang, encoder, decoder, s, device)


if __name__ == '__main__':
    # FIXME: https://stackoverflow.com/questions/53890693/cprofile-causes-pickling-error-when-running-multiprocessing-python-code
    import cProfile
    import sys
    if sys.modules['__main__'].__file__ == cProfile.__file__:
        import i_s2s_xlat2
        globals().update(vars(i_s2s_xlat2))  # Replaces current contents with newly imported stuff
        sys.modules['__main__'] = i_s2s_xlat2  # Ensures pickle lookups on __main__ find matching version

    _main()
