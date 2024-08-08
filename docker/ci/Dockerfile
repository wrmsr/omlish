FROM python:3.12.5-bookworm
COPY docker/.dockertimestamp /


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
        build-essential \
        clang \
        cmake \
        gdb \
        libdb-dev \
        llvm \
\
)


## config

COPY \
\
    docker/dev/.gdbinit \
    docker/dev/.tmux.conf \
    docker/dev/.vimrc \
\
    /root/


## entrypoint

RUN mkdir /build
WORKDIR /build

COPY requirements.txt /build/requirements.txt
COPY requirements-dev.txt /build/requirements-dev.txt
RUN pip install --quiet --progress-bar=off -r requirements-dev.txt

RUN mkdir /omlish
COPY . /omlish/

WORKDIR /omlish

CMD ["bash", "-c", "make _ci"]
