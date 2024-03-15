# -*- coding: utf-8 -*-
import argparse
import logging
import torch
from torchtext.data import TabularDataset, Field, LabelField, BucketIterator
import torch.optim as optim
import torch.nn as nn
import time
from gensim.models import KeyedVectors
import numpy as np
from preprocess.preprocess import clean_str, build_data
from model.model import CNN1d, binary_accuracy, train, evaluate, epoch_time

parser = argparse.ArgumentParser(description = 'Start training..!')
parser.add_argument('--epochs', type=int, default=10)
parser.add_argument('--data_dir', type=str, default='./preprocess')
parser.add_argument('--batch_size', type=int, default=50)
parser.add_argument('--embedding', type=int, default=300)
parser.add_argument('--n_filters', type=int, default=100)
parser.add_argument('--filter_sizes', type=list, default=[3, 4, 5])
parser.add_argument('--dropout', type=float, default=0.5)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main(args):
    print('start ..!')
    BATCH_SIZE = args.batch_size
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    TEXT = Field(sequential=True,  # text: sequential data
                 tokenize=str.split,
                 batch_first=True,
                 fix_length=56,  # padding size: max length of data text
                 lower=True)
    LABEL = LabelField(sequential=False,
                       dtype=torch.float)

    w2v = KeyedVectors.load_word2vec_format('./model/GoogleNews-vectors-negative300.bin.gz', binary=True)

    data_dir = args.data_dir

    train_paths, val_paths = build_data(data_dir)

    N_EPOCHS = args.epochs
    EMBEDDING_DIM = args.embedding
    N_FILTERS = args.n_filters
    FILTER_SIZES = args.filter_sizes
    OUTPUT_DIM = 1
    DROPOUT = args.dropout
    test_acc_lists = []

    for kfold in range(10):
        # make datasets
        train_path = train_paths[kfold]
        val_path = val_paths[kfold]
        train_data = TabularDataset(path=train_path, skip_header=True,
                                    format='csv', fields=[('label', LABEL), ('text', TEXT)])
        test_data = TabularDataset(path=val_path, skip_header=True,
                                   format='csv', fields=[('label', LABEL), ('text', TEXT)])

        TEXT.build_vocab(train_data)
        LABEL.build_vocab(train_data)

        # for pretrained embedding vectors
        w2v_vectors = []
        for token, idx in TEXT.vocab.stoi.items():
            # pad token -> zero
            if idx == 1:
                w2v_vectors.append(torch.zeros(EMBEDDING_DIM))
            # if word in word2vec vocab -> replace with pretrained word2vec
            elif token in w2v.wv.vocab.keys():
                w2v_vectors.append(torch.FloatTensor(w2v[token]))
            # oov -> randomly initialized uniform distribution
            else:
                w2v_vectors.append(torch.distributions.Uniform(-0.25, +0.25).sample((EMBEDDING_DIM,)))

        TEXT.vocab.set_vectors(TEXT.vocab.stoi, w2v_vectors, EMBEDDING_DIM)
        pretrained_embeddings = torch.FloatTensor(TEXT.vocab.vectors)

        # make iterators
        train_iterator, test_iterator = BucketIterator.splits(
            (train_data, test_data),
            batch_size=BATCH_SIZE,
            device=device, sort=False, shuffle=True)

        # define a model
        INPUT_DIM = len(TEXT.vocab)

        model = CNN1d(pretrained_embeddings, INPUT_DIM, EMBEDDING_DIM, N_FILTERS, FILTER_SIZES, OUTPUT_DIM, DROPOUT)
        optimizer = optim.Adadelta(model.parameters(), rho=0.95)
        criterion = nn.BCEWithLogitsLoss()

        model = model.to(device)
        criterion = criterion.to(device)

        # train
        best_test_acc = -float('inf')
        model_name = './model/model' + str(kfold) + '.pt'
        print('kfold', kfold)
        for epoch in range(N_EPOCHS):

            start_time = time.time()

            train_loss, train_acc = train(model, train_iterator, optimizer, criterion)
            test_loss, test_acc = evaluate(model, test_iterator, criterion)

            end_time = time.time()

            epoch_mins, epoch_secs = epoch_time(start_time, end_time)

            if test_acc > best_test_acc:
                best_test_acc = test_acc
                torch.save(model.state_dict(), model_name)

            # print(f'\tEpoch: {epoch + 1:02} | Epoch Time: {epoch_mins}m {epoch_secs}s')
            # print(f'\t\tTrain Loss: {train_loss:.3f} | Train Acc: {train_acc * 100:.2f}%')
            # print(f'\t\tTest. Loss: {test_loss:.3f} |  Val. Acc: {test_acc * 100:.2f}%')
            logging.info(f'\tEpoch: {epoch + 1:02} | Epoch Time: {epoch_mins}m {epoch_secs}s')
            logging.info(f'\t\tTrain Loss: {train_loss:.3f} | Train Acc: {train_acc * 100:.2f}%')
            logging.info(f'\t\tTest. Loss: {test_loss:.3f} |  Val. Acc: {test_acc * 100:.2f}%')

        model.load_state_dict(torch.load(model_name))

        test_loss, test_acc = evaluate(model, test_iterator, criterion)
        test_acc_lists.append(test_acc)
        logging.info(f'============== last test accuracy: {test_acc}')
        # print(f'============== last test accuracy: {test_acc}')
        print()
    return test_acc_lists


args = parser.parse_args()
logging.info(args)

if __name__ =='__main__':
    # parser = argparse.ArgumentParser(description = 'Start training..!')
    # parser.add_argument('--epochs', type=int, default=10)
    # parser.add_argument('--data_dir', type = str, default = './preprocess')
    # parser.add_argument('--batch_size', type=int, default=50)
    # parser.add_argument('--embedding', type=int, default = 300)
    # parser.add_argument('--n_filters', type=int, default=100)
    # parser.add_argument('--filter_sizes', type=list, default=[3, 4, 5])
    # parser.add_argument('--dropout', type=float, default=0.5)
    # args = parser.parse_args()

    test_acc_lists = main(args)
    print('============== 10 - fold test accuracy ==============')
    print(f'Mean acc {np.mean(test_acc_lists) * 100 :.2f}%')
    print(test_acc_lists)
    pd.DataFrame(test_acc_lists, columns={'accuracy'}).to_csv('results.csv', encodint='utf-8')