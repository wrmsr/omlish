#!/usr/bin/env bash

# apt-cache policy | grep 'origin archive.lambdalabs.com'
# echo "$RUNPOD_POD_ID"

export DEBIAN_FRONTEND=noninteractive && \
sudo apt-get update && \
sudo apt-get install -y \
        \
        btop \
        git \
        jq \
        less \
        mosh \
        ncdu \
        nvtop \
        silversearcher-ag \
        tmux \
        vim \
        \
        libdb-dev \
        \
        build-essential \
        gdb \
        lcov \
        libbz2-dev \
        libc6-dev \
        libffi-dev \
        libgdbm-compat-dev \
        libgdbm-dev \
        liblzma-dev \
        libncurses5-dev \
        libreadline6-dev \
        libsqlite3-dev \
        libssl-dev \
        lzma \
        lzma-dev \
        pkg-config \
        tk-dev \
        uuid-dev \
        zlib1g-dev \

echo "\
setw -g mode-keys vi
set -g status-keys vi
set -sg escape-time 0
set -g status-fg black
set-option -g history-limit 20000
" >> ~/.tmux.conf

echo "
set number
syntax on
filetype indent plugin on
set tabstop=4
set shiftwidth=4
set expandtab
" >> ~/.vimrc

cd ~

# tmux -2

git clone https://github.com/pyenv/pyenv .pyenv

git clone https://github.com/wrmsr/omlish && \
cd omlish && \
git submodule update --init

make venv

# btop --utf-force
# nvtop