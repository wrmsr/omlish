FROM python:3.13.5-bookworm

RUN ( \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
\
    export DEBIAN_FRONTEND=noninteractive && \
    apt update && \
    apt upgrade -y && \
    apt install -y apt-utils && \
\
    apt install -o Acquire::http::No-Cache=true -y \
\
        build-essential \
        clang \
        cmake \
        curl \
        gdb \
        iputils-ping \
        libdb-dev \
        llvm \
\
    && \
\
    apt clean autoclean && \
    apt autoremove --yes && \
    rm -rf \
        /var/cache/apt \
        /var/lib/{apt,cache,dpkg,log} \
\
)
