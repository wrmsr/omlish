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

# RUN echo "\
# [Unit] \n\
# Description=the target for docker-entrypoint.service \n\
# Requires=docker-entrypoint.service systemd-logind.service systemd-user-sessions.service \n\
# " > /etc/systemd/system/docker-entrypoint.target
#
# cat echo "\
# [Unit] \n\
# Description=docker-entrypoint.service \n\
#  \n\
# [Service] \n\
# ExecStart=/bin/bash -exc "source /etc/docker-entrypoint-cmd" \n\
# # EXIT_STATUS is either an exit code integer or a signal name string, see systemd.exec(5) \n\
# ExecStopPost=/bin/bash -ec "if echo \${EXIT_STATUS} | grep [A-Z] > /dev/null; then echo >&2 \"got signal \${EXIT_STATUS}\"; systemctl exit \$(( 128 + \$( kill -l \${EXIT_STATUS} ) )); else systemctl exit \${EXIT_STATUS}; fi" \n\
# StandardInput=tty-force \n\
# StandardOutput=inherit \n\
# StandardError=inherit \n\
# EnvironmentFile=/etc/docker-entrypoint-env \n\
#  \n\
# [Install] \n\
# WantedBy=multi-user.target \n\
# " > /etc/systemd/system/docker-entrypoint.service

RUN systemctl mask systemd-firstboot.service systemd-udevd.service systemd-modules-load.service
RUN systemctl unmask systemd-logind

# RUN systemctl enable docker-entrypoint.service

# ENTRYPOINT ["systemd", "--show-status=false", "--unit=docker-entrypoint.target"]
 # , "--unit=docker-entrypoint.target"]
CMD ["systemd", "--show-status=false"]
