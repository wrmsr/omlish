#!/usr/bin/env bash
set -ex

sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

echo "\
setw -g mode-keys vi \n\
set -g status-keys vi \n\
set -sg escape-time 0 \n\
set -g status-fg black \n\
set-option -g history-limit 20000 \n\
" >> ~/.tmux.conf

echo "\
set number \n\
syntax on \n\
filetype indent plugin on \n\
set tabstop=4 \n\
set shiftwidth=4 \n\
set expandtab \n\
" >> ~/.vimrc

git clone "https://github.com/pyenv/pyenv" "$HOME/.pyenv"
