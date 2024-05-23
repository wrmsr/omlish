import collections
import os

from torch.utils.data import DataLoader
import torch
import torchtext


def _main():
    os.makedirs('./data', exist_ok=True)

    classes = ['World', 'Sports', 'Business', 'Sci/Tech']
    train_dataset, test_dataset = torchtext.datasets.AG_NEWS(root='./data')

    train_dataset = list(train_dataset)
    test_dataset = list(test_dataset)

    tokenizer = torchtext.data.utils.get_tokenizer('basic_english')
    counter = collections.Counter()
    for label, line in train_dataset:
        counter.update(tokenizer(line))

    vocab = torchtext.vocab.vocab(counter)
    stoi = vocab.get_stoi()  # dict to convert tokens to indices

    def encode(x):
        return [stoi[s] for s in tokenizer(x)]

    vocab_size = len(vocab)

    def to_bow(text, bow_vocab_size=vocab_size):
        res = torch.zeros(bow_vocab_size, dtype=torch.float32)
        for i in encode(text):
            if i < bow_vocab_size:
                res[i] += 1
        return res

    # this collate function gets list of batch_size tuples, and needs to return a pair of label-feature tensors for the
    # whole minibatch
    def bowify(b):
        return (
            torch.LongTensor([t[0] - 1 for t in b]),
            torch.stack([to_bow(t[1]) for t in b])
        )

    train_loader = DataLoader(train_dataset, batch_size=16, collate_fn=bowify, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=16, collate_fn=bowify, shuffle=True)

    net = torch.nn.Sequential(
        torch.nn.Linear(vocab_size, 4),
        torch.nn.LogSoftmax(dim=1),
    )

    def train_epoch(
            net,
            dataloader,
            lr=0.01,
            optimizer=None,
            loss_fn=torch.nn.NLLLoss(),
            epoch_size=None,
            report_freq=200,
    ):
        optimizer = optimizer or torch.optim.Adam(net.parameters(), lr=lr)
        net.train()
        total_loss, acc, count, i = 0, 0, 0, 0
        for labels, features in dataloader:
            optimizer.zero_grad()
            out = net(features)
            loss = loss_fn(out, labels)  # cross_entropy(out,labels)
            loss.backward()
            optimizer.step()
            total_loss += loss
            _, predicted = torch.max(out, 1)
            acc += (predicted == labels).sum()
            count += len(labels)
            i += 1
            if i % report_freq == 0:
                print(f"{count}: acc={acc.item() / count}")
            if epoch_size and count > epoch_size:
                break
        return total_loss.item() / count, acc.item() / count

    train_epoch(net, train_loader, epoch_size=15000)


if __name__ == '__main__':
    _main()
