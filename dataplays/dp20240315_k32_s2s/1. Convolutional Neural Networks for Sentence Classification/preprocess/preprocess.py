import os
import sys, re
import numpy as np
import pandas as pd
import pickle
import codecs
import random
import json

SEED = 3435
random.seed(SEED)
np.random.seed(SEED)


## clean_str: preprocess from original source code: https://github.com/yoonkim/CNN_sentence
def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Every dataset is lower cased except for TREC
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


def build_data(data_dir):
    '''
    build data for 10 fold
    '''
    revs = []
    train_paths = []
    val_paths = []
    
    pos = codecs.open(os.path.join(data_dir, "rt-polarity.pos"), "r", encoding='utf-8', errors='ignore').read()
    neg = codecs.open(os.path.join(data_dir, "rt-polarity.neg"), "r", encoding='utf-8', errors='ignore').read()
    pos_list = [clean_str(sent) for sent in pos.split('\n')[:-1]]
    neg_list = [clean_str(sent) for sent in neg.split('\n')[:-1]]

    cv = 10
    for sent in pos_list:
        datum = {'label': 1,
                 'text': sent,
                 'split': np.random.randint(0, cv)  # 10-kfold allocation
                 }
        revs.append(datum)

    for sent in neg_list:
        datum = {'label': 0,
                 'text': sent,
                 'split': np.random.randint(0, cv)  # 10-kfold allocation
                 }
        revs.append(datum)


    df = pd.DataFrame(revs)
    for kfold in range(10):
        train = df[df['split'] != kfold]
        val = df[df['split'] == kfold]

        print(f'save the kfold {kfold} data')
        train_path = './preprocess/train' + str(kfold) + '.csv'
        val_path = './preprocess/val' + str(kfold) + '.csv'
        train.to_csv(train_path, index=False, encoding='utf-8')
        val.to_csv(val_path, index=False, encoding='utf-8')
        train_paths.append(train_path)
        val_paths.append(val_path)
    return train_paths, val_paths