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
        supervisor \
\
)

RUN ( \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt install -y \
\
        python3.12-dev \
        python3.12-full \
\
)

#

RUN rm /etc/nginx/sites-enabled/default

RUN mkdir -p /var/log/supervisor

RUN echo "\
[supervisord] \n\
nodaemon=true \n\
logfile=/var/log/supervisor/supervisor.log \n\
logfile_maxbytes=4194304 \n\
\n\
[program:app] \n\
command = sleep infinity \n\
stdout_logfile=/dev/fd/1 \n\
stdout_logfile_maxbytes=0 \n\
redirect_stderr=true \n\
" > /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
