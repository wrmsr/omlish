import collections

import numpy as np
import torch
import torchtext


def _main() -> None:
    classes = ['World', 'Sports', 'Business', 'Sci/Tech']
    train_dataset, test_dataset = torchtext.datasets.AG_NEWS(root='./data')

    tokenizer = torchtext.data.utils.get_tokenizer('basic_english')
    counter = collections.Counter()
    for label, line in train_dataset:
        counter.update(tokenizer(line))

    vocab = torchtext.vocab.vocab(counter)
    stoi = vocab.get_stoi()  # dict to convert tokens to indices

    def encode(x):
        return [stoi[s] for s in tokenizer(x)]

    vocab_size = len(vocab)

    class EmbedClassifier(torch.nn.Module):
        def __init__(self, vocab_size, embed_dim, num_class):
            super().__init__()
            self.embedding = torch.nn.Embedding(vocab_size, embed_dim)
            self.fc = torch.nn.Linear(embed_dim, num_class)

        def forward(self, x):
            x = self.embedding(x)
            x = torch.mean(x, dim=1)
            return self.fc(x)

    def padify(b):
        # b is the list of tuples of length batch_size
        #   - first element of a tuple = label,
        #   - second = feature (text sequence)
        # build vectorized sequence
        v = [encode(x[1]) for x in b]
        # first, compute max length of a sequence in this minibatch
        l = max(map(len, v))
        return (  # tuple of two tensors - labels and features
            torch.LongTensor([t[0] - 1 for t in b]),
            torch.stack([
                torch.nn.functional.pad(torch.tensor(t), (0, l - len(t)), mode='constant', value=0)
                for t in v
            ])
        )

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=16, collate_fn=padify, shuffle=True)

    device = 'cpu'

    net = EmbedClassifier(vocab_size, 32, len(classes)).to(device)

    def train_epoch(
            net,
            dataloader,
            lr=0.01,
            optimizer=None,
            loss_fn=torch.nn.NLLLoss(),
            epoch_size=None,
            report_freq=200,
    ) -> tuple[float, float]:
        optimizer = optimizer or torch.optim.Adam(net.parameters(), lr=lr)

        net.train()

        total_loss = torch.tensor(0.).to(device)
        acc = torch.tensor(0).to(device)
        count = 0
        i = 0

        for labels, features in dataloader:
            labels = labels.to(device)
            features = features.to(device)

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

    # while True:
    #     train_epoch(net, train_loader, lr=1, epoch_size=25000)

    ##

    class EmbedClassifier(torch.nn.Module):
        def __init__(self, vocab_size, embed_dim, num_class):
            super().__init__()
            self.embedding = torch.nn.EmbeddingBag(vocab_size, embed_dim)
            self.fc = torch.nn.Linear(embed_dim, num_class)

        def forward(self, text, off):
            x = self.embedding(text, off)
            return self.fc(x)

    def offsetify(b):
        # first, compute data tensor from all sequences
        x = [torch.tensor(encode(t[1])) for t in b]
        # now, compute the offsets by accumulating the tensor of sequence lengths
        o = [0] + [len(t) for t in x]
        o = torch.tensor(o[:-1]).cumsum(dim=0)
        return (
            torch.LongTensor([t[0] - 1 for t in b]),  # labels
            torch.cat(x),  # text
            o
        )

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=16, collate_fn=offsetify, shuffle=True)

    net = EmbedClassifier(vocab_size, 32, len(classes)).to(device)

    def all_to(device, *ts):
        return [t.to(device) for t in ts]

    def train_epoch_emb(
            net,
            dataloader,
            lr=0.01,
            optimizer=None,
            loss_fn=torch.nn.CrossEntropyLoss(),
            epoch_size=None,
            report_freq=200,
    ):
        optimizer = optimizer or torch.optim.Adam(net.parameters(), lr=lr)
        loss_fn = loss_fn.to(device)
        net.train()

        total_loss, acc, count, i = 0, 0, 0, 0
        for labels, text, off in dataloader:
            optimizer.zero_grad()
            labels, text, off = all_to(device, labels, text, off)
            out = net(text, off)
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

    for _ in range(4):
        train_epoch_emb(net, train_loader, lr=4, epoch_size=25000)

    # net.eval()
    #
    # print(net)
    #
    # word_weights = net.embedding.weight.data
    #
    # words = vocab.get_itos()
    #
    # word_lengths = np.linalg.norm(word_weights, axis=1)
    # normalized_words = (word_weights.T / word_lengths).T
    #
    # def similar_words(word):
    #     dists = np.dot(normalized_words, normalized_words[stoi[word]])
    #     closest = np.argsort(dists)[-10:]
    #     for c in reversed(closest):
    #         print(c, words[c], dists[c])
    #
    # print(similar_words('cat'))


if __name__ == '__main__':
    _main()
