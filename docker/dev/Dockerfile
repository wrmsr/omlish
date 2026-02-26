FROM ubuntu:24.04


## locale

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8


## deps

RUN \
  --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
  --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
set -ex ;\
\
rm -f /etc/apt/apt.conf.d/docker-clean ;\
\
export DEBIAN_FRONTEND=noninteractive ;\
apt-get update ;\
\
apt-get install -y locales ;\
locale-gen en_US.UTF-8 ;\
\
apt-get upgrade -y ;\
apt-get install -y apt-utils ;\
\
DEPS="" ;\
\
# system\
\
DEPS="$DEPS\
  apt-transport-https\
  aria2\
  bison\
  bmon\
  btop\
  build-essential\
  ca-certificates\
  clang\
  cmake\
  curl\
  cvs\
  dnsutils\
  dumb-init\
  emacs\
  file\
  flex\
  g++\
  g++-14\
  gcc\
  gcc-14\
  gdb\
  git\
  gnupg\
  gnupg-agent\
  graphviz\
  htop\
  iputils-ping\
  iputils-tracepath\
  irssi\
  jq\
  less\
  libdb-dev\
  libpq-dev\
  llvm\
  lsb-release\
  lsof\
  make\
  man-db\
  maven\
  mercurial\
  moreutils\
  mosh\
  nano\
  ncdu\
  net-tools\
  netcat-openbsd\
  openssh-server\
  perl\
  pkg-config\
  postgresql-client\
  protobuf-compiler\
  ripgrep\
  ruby\
  silversearcher-ag\
  socat\
  software-properties-common\
  strace\
  subversion\
  sudo\
  tcpdump\
  telnet\
  tmux\
  unzip\
  vim\
  wget\
  xsltproc\
  zip\
  zsh\
" ;\
\
# python\
\
DEPS="$DEPS\
  build-essential\
  gdb\
  lcov\
  libbz2-dev\
  libffi-dev\
  libgdbm-compat-dev\
  libgdbm-dev\
  liblzma-dev\
  libncurses5-dev\
  libreadline6-dev\
  libsqlite3-dev\
  libssl-dev\
  lzma\
  lzma-dev\
  pkg-config\
  tk-dev\
  uuid-dev\
  zlib1g-dev\
" ;\
\
# x11\
\
DEPS="$DEPS\
  x11-apps\
" ;\
\
apt-get install -y $DEPS\
)


## firefox

RUN \
  --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
  --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
set -ex ;\
\
add-apt-repository ppa:mozillateam/ppa ;\
\
echo "\
Package: *\n\
Pin: release o=LP-PPA-mozillateam\n\
Pin-Priority: 1001\n\
\n\
Package: firefox\n\
Pin: version 1:1snap1-0ubuntu2\n\
Pin-Priority: -1\n\
" | sudo tee /etc/apt/preferences.d/mozilla-firefox ;\
\
apt-get update ;\
apt-get install -y firefox ;\
\
echo 'Unattended-Upgrade::Allowed-Origins:: "LP-PPA-mozillateam:${distro_codename}";' |\
  sudo tee /etc/apt/apt.conf.d/51unattended-upgrades-firefox ;\
)


## docker

RUN \
  --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
  --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
set -ex ;\
\
mkdir -p /etc/apt/keyrings ;\
curl -fsSL 'https://download.docker.com/linux/ubuntu/gpg' | gpg --dearmor -o /etc/apt/keyrings/docker.gpg ;\
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu\
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null ;\
\
apt-get update ;\
apt-get install -y docker-ce-cli ;\
)


## jdk

RUN \
  --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
  --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
export JDKS='zulu21-ca-jdk zulu25-ca-jdk' ;\
\
set -ex ;\
\
sudo apt install gnupg ca-certificates curl ;\
curl -s 'https://repos.azul.com/azul-repo.key' | sudo gpg --dearmor -o /usr/share/keyrings/azul.gpg ;\
echo "deb [signed-by=/usr/share/keyrings/azul.gpg] https://repos.azul.com/zulu/deb stable main" | sudo tee /etc/apt/sources.list.d/zulu.list ;\
\
apt-get update ;\
apt-get install -y ${JDKS} ;\
)


## rust

RUN (\
set -ex ;\
\
curl --proto '=https' --tlsv1.2 -sSf 'https://sh.rustup.rs' | sh -s -- -y ;\
\
$HOME/.cargo/bin/cargo install \
\
  cargo-edit \
  rust-script \
\
;\
)


## go

RUN (\
export GO_VERSION='1.26.0' ;\
\
set -ex ;\
\
curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-$(dpkg --print-architecture).tar.gz" | tar -C "$HOME" -xzf - ;\
mv "$HOME/go" "$HOME/.go" ;\
\
echo '\n\
export GOROOT="$HOME/.go"\n\
export PATH="$GOROOT/bin:$PATH"\n\
' >> ~/.bashrc ;\
)


## zig

RUN (\
export ZIG_VERSION='0.15.2' ;\
\
set -ex ;\
\
curl -fsSL "https://ziglang.org/download/${ZIG_VERSION}/zig-$(uname -m)-linux-${ZIG_VERSION}.tar.xz" | tar -xJ -C "$HOME" ;\
mv "$HOME/zig-$(uname -m)-linux-${ZIG_VERSION}" "$HOME/.zig" ;\
\
echo '\n\
export PATH="$HOME/.zig:$PATH"\n\
' >> ~/.bashrc ;\
)


## vcpkg

RUN (\
set -ex ;\
\
git clone 'https://github.com/microsoft/vcpkg' /root/.vcpkg_root ;\
(cd /root/.vcpkg_root && ./bootstrap-vcpkg.sh) ;\
\
echo '\n\
export VCPKG_ROOT="$HOME/.vcpkg_root"\n\
' >> ~/.bashrc ;\
)


## nvm

RUN (\
export NVM_VERSIONS='20 22 25' ;\
\
set -ex ;\
\
curl -o- 'https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh' | bash ;\
\
export NVM_DIR="$HOME/.nvm" ;\
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" ;\
\
for NV in ${NVM_VERSIONS} ; do\
  nvm install "$NV" ;\
done ;\
)


## uv

RUN (\
set -ex ;\
\
curl -LsSf 'https://astral.sh/uv/install.sh' | sh ;\
)


## pyenv

RUN \
  --mount=target=/root/.pyenv_cache,type=cache,sharing=locked \
( \
export PYENV_VERSIONS='3.8.20 3.13.12 3.14.3' ;\
\
set -ex ;\
\
git clone 'https://github.com/pyenv/pyenv' /root/.pyenv ;\
\
for V in ${PYENV_VERSIONS} ; do\
  PYTHON_BUILD_CACHE_PATH=/root/.pyenv_cache /root/.pyenv/bin/pyenv install -s "$V" ;\
done ;\
)


## sshd

RUN (\
set -ex ;\
\
sed -i 's/^#*PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config ;\
sed -i 's/^#X11UseLocalhost yes/X11UseLocalhost no/' /etc/ssh/sshd_config ;\
sed -i 's/^# Ciphers and keying/Ciphers chacha20-poly1305@openssh.com/' /etc/ssh/sshd_config ;\
sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd ;\
mkdir /var/run/sshd ;\
)


## configs

RUN echo '\
handle SIGUSR1 nostop noprint\n\
handle SIGUSR2 nostop noprint\n\
' > /root/.gdbinit

RUN echo '\
setw -g mode-keys vi\n\
set -g status-keys vi\n\
set -sg escape-time 0\n\
set -g status-fg black\n\
set -g history-limit 50000\n\
set -g update-environment "DISPLAY"\n\
set -sg default-terminal "xterm-256color"\n\
' > /root/.tmux.conf

RUN echo '\
set number\n\
syntax on\n\
filetype indent plugin on\n\
set tabstop=4\n\
set shiftwidth=4\n\
set expandtab\n\
' > /root/.vimrc


## entrypoint

WORKDIR /omlish

ENTRYPOINT [ \
  "dumb-init", \
  "--" \
]

CMD [ \
  "sh", \
  "-c", \
  "echo \"Ready\" && sleep infinity" \
]
