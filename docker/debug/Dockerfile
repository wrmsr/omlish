FROM python:3.12.4-bookworm
COPY docker/.dockertimestamp /


## deps

RUN ( \
\
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


## entrypoint

RUN mkdir /build
WORKDIR /build

COPY requirements.txt /build/requirements.txt
COPY requirements-dev.txt /build/requirements-dev.txt
RUN pip install --quiet --progress-bar=off -r requirements-dev.txt
