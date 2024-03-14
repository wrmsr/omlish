import pickle

import torch


def convert_data(batch, vocab, device, reverse=False, unk=None, pad=None, sos=None, eos=None):
    max_len = max(len(x) for x in batch)
    padded = []
    for x in batch:
        if reverse:
            padded.append(
                ([] if eos is None else [eos]) +
                list(x[::-1]) +
                ([] if sos is None else [sos]))
        else:
            padded.append(
                ([] if sos is None else [sos]) +
                list(x) +
                ([] if eos is None else [eos]))
        padded[-1] = padded[-1] + [pad] * max(0, max_len - len(x))
        padded[-1] = list(map(lambda v: vocab['stoi'][v] if v in vocab['stoi'] else vocab['stoi'][unk], padded[-1]))
    padded = torch.LongTensor(padded).to(device)
    mask = padded.ne(vocab['stoi'][pad]).float()
    return padded, mask


def convert_str(batch, vocab):
    output = []
    for x in batch:
        output.append(list(map(lambda v: vocab['itos'][v], x)))
    return output


def invert_vocab(vocab):
    v = {}
    for k, idx in vocab.items():
        v[idx] = k
    return v


def load_vocab(path):
    f = open(path, 'rb')
    vocab = pickle.load(f)
    f.close()
    return vocab


def sort_batch(batch):
    batch = zip(*batch)
    batch = sorted(batch, key=lambda x: len(x[0]), reverse=True)
    batch = zip(*batch)
    return list(batch)

