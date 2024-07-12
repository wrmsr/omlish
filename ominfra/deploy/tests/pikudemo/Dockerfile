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
        nginx \
        openssh-server \
        openssl \
        python3 \
        tmux \
        vim \
        wget \
\
        ansible \
\
        python3-apt \
\
        bc \
        git \
        sudo \
        cron \
        build-essential \
        libpcre3-dev \
        zlib1g-dev \
        python3 \
        python3-pip \
        python3-click \
        python3-dev \
        python3-virtualenv \
        python3-setuptools \
        nginx \
        acl \
        uwsgi-core \
        uwsgi-plugin-python3 \
        nodeenv \
\
        ieee-data \
        python-babel-localedata \
        python3-argcomplete \
        python3-babel \
        python3-certifi \
        python3-cffi-backend \
        python3-chardet \
        python3-cryptography \
        python3-dnspython \
        python3-httplib2 \
        python3-idna \
        python3-jinja2 \
        python3-jmespath \
        python3-kerberos \
        python3-libcloud \
        python3-lockfile \
        python3-markupsafe \
        python3-netaddr \
        python3-ntlm-auth \
        python3-packaging \
        python3-pycryptodome \
        python3-pyparsing \
        python3-requests \
        python3-requests-kerberos \
        python3-requests-ntlm \
        python3-requests-toolbelt \
        python3-selinux \
        python3-simplejson \
        python3-tz \
        python3-urllib3 \
        python3-winrm \
        python3-xmltodict \
        python3-yaml \
\
)

ENTRYPOINT ["dumb-init", "--"]
CMD ["sh", "-c", "echo 'Ready' && sleep infinity"]
