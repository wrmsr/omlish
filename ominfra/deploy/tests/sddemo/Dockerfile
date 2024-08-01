FROM ubuntu:22.04

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
    TZ=Etc/UTC apt-get install -y tzdata && \
\
    apt-get install -y \
\
        curl \
        dumb-init \
        git \
        make \
        nginx \
        openssl \
        python3 \
        python3-pip \
        python3-venv \
        software-properties-common \
        tmux \
        vim \
        wget \
\
        dbus \
        dbus-user-session \
        systemd \
        systemd-sysv \
\
)

ENTRYPOINT ["dumb-init", "--"]
CMD ["sh", "-c", "echo 'Ready' && sleep infinity"]
