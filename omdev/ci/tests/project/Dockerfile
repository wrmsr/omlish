FROM python:3.12.8-bookworm

RUN ( \
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
        curl \
        gdb \
        libdb-dev \
        llvm \
\
    && \
\
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log} \
)
