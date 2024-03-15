import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import time


class CNN1d(nn.Module):
    def __init__(self, pretrained_embedding, vocab_size, embedding_dim, n_filters, filter_sizes, output_dim,
                 dropout):
        super().__init__()

        # static: static through training
        self.static_emd = nn.Embedding.from_pretrained(pretrained_embedding.clone().detach())
        # non-static: fine-tuning via backpropagation
        self.nonstatic_emd = nn.Embedding.from_pretrained(pretrained_embedding.clone().detach(), freeze=False)

        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embedding_dim,
                      out_channels=n_filters,
                      kernel_size=fs,
                      padding=(fs - 1))
            for fs in filter_sizes
        ])

        self.fc = nn.Linear(6 * n_filters, output_dim)

        self.dropout = nn.Dropout(dropout)

    def forward(self, text):
        # text = [batch size, sent len]
        #         print('text', text.shape)
        static_emb = self.static_emd(text)
        static_emb = static_emb.permute(0, 2, 1)
        #         print('static_emb', static_emb.shape)
        static_conved = [F.relu(conv(static_emb)) for conv in self.convs]
        #         print('conved', len(static_conved))
        #         print('** conved[0]', static_conved[0].shape)
        #         print('** conved[1]', static_conved[1].shape)
        #         print('** conved[2]', static_conved[2].shape)
        static_pooled = [F.max_pool1d(conv, conv.shape[2]).squeeze(2) for conv in static_conved]
        #         print('static_pooled', len(static_pooled))
        #         print('** static_pooled[0]',static_pooled[0].shape)
        #         print('** static_pooled[1]',static_pooled[1].shape)
        #         print('** static_pooled[2]',static_pooled[2].shape)

        non_static_emb = self.nonstatic_emd(text)
        non_static_emb = non_static_emb.permute(0, 2, 1)
        non_static_conved = [F.relu(conv(non_static_emb)) for conv in self.convs]
        #         print('non_static_conved', len(non_static_conved))
        #         print('** non_static_conved[0]', non_static_conved[0].shape)
        #         print('** non_static_conved[1]', non_static_conved[1].shape)
        #         print('** non_static_conved[2]', non_static_conved[2].shape)
        non_static_pooled = [F.max_pool1d(conv, conv.shape[2]).squeeze(2) for conv in non_static_conved]

        pooled = static_pooled + non_static_pooled
        cat = self.dropout(torch.cat(pooled, dim=1))
        #         print('cat', cat.shape)
        # cat = [batch size, n_filters * len(filter_sizes)]
        #         print('self.fc(cat)', self.fc(cat).shape)
        #         print('***********************************************')
        return self.fc(cat)


def binary_accuracy(preds, y):
    """
    Returns accuracy per batch, i.e. if you get 8/10 right, this returns 0.8, NOT 8
    """

    #round predictions to the closest integer
    rounded_preds = torch.round(torch.sigmoid(preds))
    correct = (rounded_preds == y).float() #convert into float for division
    acc = correct.sum() / len(correct)
    return acc


def train(model, iterator, optimizer, criterion):
    epoch_loss = 0
    epoch_acc = 0

    model.train()

    for batch in iterator:

        optimizer.zero_grad()

        predictions = model(batch.text).squeeze(1)
        loss = criterion(predictions, batch.label)
        acc = binary_accuracy(predictions, batch.label)

        loss.backward()
        optimizer.step()

        #  l2 norm (weight contraints): 3
        for name, param in model.named_parameters():
            if 'fc.weight' in name:
                max_val = 3
                norm = param.norm(dim=0, keepdim=True)
                desired = torch.clamp(norm, 0, max_val)
                scale = desired / (1e-7 + norm)
                param.data.copy_(param * scale)

        epoch_loss += loss.item()
        epoch_acc += acc.item()

    return epoch_loss / len(iterator), epoch_acc / len(iterator)


def evaluate(model, iterator, criterion):
    epoch_loss = 0
    epoch_acc = 0

    model.eval()

    with torch.no_grad():
        for batch in iterator:
            predictions = model(batch.text).squeeze(1)

            loss = criterion(predictions, batch.label)

            acc = binary_accuracy(predictions, batch.label)

            epoch_loss += loss.item()
            epoch_acc += acc.item()

    return epoch_loss / len(iterator), epoch_acc / len(iterator)


def epoch_time(start_time, end_time):
    elapsed_time = end_time - start_time
    elapsed_mins = int(elapsed_time / 60)
    elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
    return elapsed_mins, elapsed_secs
