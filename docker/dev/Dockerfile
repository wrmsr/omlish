FROM ubuntu:22.04
COPY docker/.timestamp /


## deps

RUN \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
\
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y apt-utils && \
\
    apt-get install -y \
\
        apt-transport-https \
        aria2 \
        bison \
        bmon \
        btop \
        build-essential \
        ca-certificates \
        clang \
        cmake \
        curl \
        cvs \
        dnsutils \
        dumb-init \
        emacs \
        file \
        flex \
        gcc \
        gdb \
        git \
        gnupg \
        gnupg-agent \
        graphviz \
        htop \
        iputils-ping \
        iputils-tracepath \
        irssi \
        jq \
        less \
        libdb-dev \
        libpq-dev \
        llvm \
        lsb-release \
        lsof \
        make \
        man-db \
        mercurial \
        moreutils \
        mosh \
        nano \
        ncdu \
        net-tools \
        netcat \
        nodejs \
        npm \
        openssh-server \
        perl \
        pkg-config \
        postgresql-client \
        protobuf-compiler \
        ruby \
        silversearcher-ag \
        socat \
        software-properties-common \
        strace \
        subversion \
        sudo \
        tcpdump \
        telnet \
        tmux \
        unzip \
        vim \
        wget \
        xsltproc  \
        zip \
        zsh \
\
        build-essential \
        gdb \
        lcov \
        libbz2-dev \
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
\
        x11-apps \
\
)


## firefox

RUN \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
    add-apt-repository ppa:mozillateam/ppa && \
    echo "\
Package: * \n\
Pin: release o=LP-PPA-mozillateam \n\
Pin-Priority: 1001 \n\
\n\
Package: firefox \n\
Pin: version 1:1snap1-0ubuntu2 \n\
Pin-Priority: -1 \n\
" | sudo tee /etc/apt/preferences.d/mozilla-firefox && \
    apt-get update && \
    apt-get install -y firefox && \
    echo 'Unattended-Upgrade::Allowed-Origins:: "LP-PPA-mozillateam:${distro_codename}";' | \
    sudo tee /etc/apt/apt.conf.d/51unattended-upgrades-firefox \
)


## docker

RUN \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL 'https://download.docker.com/linux/ubuntu/gpg' | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli \
)


## jdk

RUN \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
    add-apt-repository ppa:openjdk-r/ppa && \
    apt-get update && \
    apt-get install -y \
    \
        openjdk-21-jdk \
    \
)

RUN ( \
    # https://stackoverflow.com/questions/6784463/error-trustanchors-parameter-must-be-non-empty \
    /usr/bin/printf '\xfe\xed\xfe\xed\x00\x00\x00\x02\x00\x00\x00\x00\xe2\x68\x6e\x45\xfb\x43\xdf\xa4\xd9\x92\xdd\x41\xce\xb6\xb2\x1c\x63\x30\xd7\x92' > /etc/ssl/certs/java/cacerts && \
    /var/lib/dpkg/info/ca-certificates-java.postinst configure \
)


## rustup

RUN ( \
    curl --proto '=https' --tlsv1.2 -sSf 'https://sh.rustup.rs' | sh -s -- -y && \
    echo "\n\
source ~/.cargo/env \n\
\n\
" >> ~/.bashrc \
)


## vcpkg

RUN ( \
    git clone 'https://github.com/microsoft/vcpkg' /root/.vcpkg_root && \
    (cd /root/.vcpkg_root && ./bootstrap-vcpkg.sh) && \
    echo "\n\
export VCPKG_ROOT="$HOME/.vcpkg_root" \n\
\n\
" >> ~/.bashrc \
)


## versions

COPY .versions /root/


## python

RUN \
    --mount=target=/root/.pyenv_cache,type=cache,sharing=locked \
( \
    git clone 'https://github.com/pyenv/pyenv' /root/.pyenv && \
    grep '^PYTHON_' /root/.versions | while read L ; do \
        K=$(echo "$L" | cut -d= -f1 | cut -d_ -f2-) && \
        case $K in \
            13) true ;; \
            *) continue ;; \
        esac && \
        echo "Installing Python $K" && \
        V=$(echo "$L" | cut -d= -f2) && \
        PYTHON_BUILD_CACHE_PATH=/root/.pyenv_cache /root/.pyenv/bin/pyenv install -s "$V" ; \
    done \
)


## config

RUN ( \
    sed -i 's/^#*PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/^#X11UseLocalhost yes/X11UseLocalhost no/' /etc/ssh/sshd_config && \
    sed -i 's/^# Ciphers and keying/Ciphers chacha20-poly1305@openssh.com/' /etc/ssh/sshd_config && \
    sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd && \
    mkdir /var/run/sshd \
)

RUN touch /root/.Xauthority

COPY \
\
    docker/dev/.gdbinit \
    docker/dev/.tmux.conf \
    docker/dev/.vimrc \
    docker/dev/xu \
\
    /root/


## entrypoint

WORKDIR /omlish

ENTRYPOINT ["dumb-init", "--"]
CMD ["sh", "-c", "echo 'Ready' && sleep infinity"]
