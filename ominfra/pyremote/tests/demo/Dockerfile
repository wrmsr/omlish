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
        openssh-server \
        openssl \
        python3 \
        python3-pip \
        python3-venv \
        software-properties-common \
        tmux \
        vim \
        wget \
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

RUN mkdir /var/run/sshd

RUN sed -i 's/#*PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd

EXPOSE 22

RUN echo "\
#!/usr/bin/env bash \n\
set -e \n\
 \n\
if [ \"x\$SSH_PASSWORD\" == \"x\" ] ; then \n\
    echo \"Must set SSH_PASSWORD\" >&2 \n\
    exit 1 \n\
fi \n\
 \n\
echo \"root:\$SSH_PASSWORD\" | chpasswd \n\
/usr/sbin/sshd -D \n\
" > /home/docker-entrypoint.sh
RUN chmod a+x /home/docker-entrypoint.sh

ENTRYPOINT ["dumb-init", "--"]
CMD ["/home/docker-entrypoint.sh"]
