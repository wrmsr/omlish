FROM ubuntu:24.04


## timestamp

COPY docker/.timestamp /


## locale

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8


## firefox

RUN \
  --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
  --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
set -ex\
\
add-apt-repository ppa:mozillateam/ppa\
\
echo "\
Package: *\n\
Pin: release o=LP-PPA-mozillateam\n\
Pin-Priority: 1001\n\
\n\
Package: firefox\n\
Pin: version 1:1snap1-0ubuntu2\n\
Pin-Priority: -1\n\
" | sudo tee /etc/apt/preferences.d/mozilla-firefox\
\
apt-get update\
apt-get install -y firefox\
\
echo 'Unattended-Upgrade::Allowed-Origins:: "LP-PPA-mozillateam:${distro_codename}";' |\
  sudo tee /etc/apt/apt.conf.d/51unattended-upgrades-firefox\
)


## docker

RUN \
  --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
  --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
set -ex\
\
mkdir -p /etc/apt/keyrings\
curl -fsSL 'https://download.docker.com/linux/ubuntu/gpg' | gpg --dearmor -o /etc/apt/keyrings/docker.gpg\
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu\
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null\
\
apt-get update\
apt-get install -y docker-ce-cli\
)


## jdk

RUN \
  --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
  --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
set -ex\
\
sudo apt install gnupg ca-certificates curl\
curl -s https://repos.azul.com/azul-repo.key | sudo gpg --dearmor -o /usr/share/keyrings/azul.gpg\
echo "deb [signed-by=/usr/share/keyrings/azul.gpg] https://repos.azul.com/zulu/deb stable main" | sudo tee /etc/apt/sources.list.d/zulu.list\
\
apt-get update\
apt-get install -y zulu21-ca-jdk zulu25-ca-jdk\
)


## rustup

RUN (\
set -ex\
\
curl --proto '=https' --tlsv1.2 -sSf 'https://sh.rustup.rs' | sh -s -- -y\
)


## go

RUN (\
set -ex\
\
curl -fsSL "https://go.dev/dl/go1.25.6.linux-$(dpkg --print-architecture).tar.gz" | tar -C "$HOME" -xzf -\
mv "$HOME/go" "$HOME/.go"\
\
echo '\n\
export GOROOT="$HOME/.go"\n\
export PATH="$GOROOT/bin:$PATH"\n\
' >> ~/.bashrc\
)


## zig

RUN (\
set -ex\
\
curl -fsSL "https://ziglang.org/download/0.15.2/zig-$(uname -m)-linux-0.15.2.tar.xz" | tar -xJ -C "$HOME"\
mv "$HOME/zig-$(uname -m)-linux-0.15.2" "$HOME/.zig"\
\
echo '\n\
export PATH="$HOME/.zig:$PATH"\n\
' >> ~/.bashrc\
)


## vcpkg

RUN (\
set -ex\
\
git clone 'https://github.com/microsoft/vcpkg' /root/.vcpkg_root\
(cd /root/.vcpkg_root && ./bootstrap-vcpkg.sh)\
\
echo '\n\
export VCPKG_ROOT="$HOME/.vcpkg_root"\n\
' >> ~/.bashrc\
)


## sshd

RUN (\
set -ex\
\
sed -i 's/^#*PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config\
sed -i 's/^#X11UseLocalhost yes/X11UseLocalhost no/' /etc/ssh/sshd_config\
sed -i 's/^# Ciphers and keying/Ciphers chacha20-poly1305@openssh.com/' /etc/ssh/sshd_config\
sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd\
mkdir /var/run/sshd\
)


## x11

RUN (\
touch /root/.Xauthority\
)

RUN echo '\
#!/usr/bin/env bash\n\
set -e\n\
\n\
if [ "\$EUID" -ne 0 ] ; then\n\
    echo "run as root"\n\
    exit 1\n\
fi\n\
\n\
if [ "\$#" == "0" ]; then\n\
    echo "run with username"\n\
    exit 1\n\
fi\n\
\n\
U="\$1"\n\
shift\n\
\n\
if ! id "\$U" &> /dev/null ; then\n\
    useradd -m "\$U"\n\
fi\n\
\n\
declare -a FS=(\n\
    ".gdbinit"\n\
    ".tmux.conf"\n\
    ".vimrc"\n\
    ".Xauthority"\n\
)\n\
\n\
for F in \${FS[@]}; do\n\
    if [ -f "\$HOME/\$F" ] && [ ! -f "/home/\$U/\$F" ] ; then\n\
        cp "\$HOME/\$F" "/home/\$U/\$F"\n\
        chown "\$U" "/home/\$U/\$F"\n\
        chgrp "\$U" "/home/\$U/\$F"\n\
    fi\n\
done\n\
\n\
if [ -f "\$HOME/.Xauthority" ] ; then\n\
    cp "\$HOME/.Xauthority" "/home/\$U/.Xauthority"\n\
    chown "\$U" "/home/\$U/.Xauthority"\n\
    chgrp "\$U" "/home/\$U/.Xauthority"\n\
fi\n\
\n\
if [ "\$#" != "0" ]; then\n\
    exec sudo -u "\$U" bash --login -c "\$*"\n\
fi\n\
' > /root/xu


## configs

RUN echo '\
handle SIGUSR1 nostop noprint\n\
handle SIGUSR2 nostop noprint\n\
' > /root/.gdbinit

RUN echo '\
setw -g mode-keys vi\n\
set -g status-keys vi\n\
set -sg escape-time 0\n\
set -g status-fg black\n\
set -g history-limit 50000\n\
set -g update-environment "DISPLAY"\n\
set -sg default-terminal "xterm-256color"\n\
' > /root/.tmux.conf

RUN echo '\
set number\n\
syntax on\n\
filetype indent plugin on\n\
set tabstop=4\n\
set shiftwidth=4\n\
set expandtab\n\
' > /root/.vimrc


## entrypoint

WORKDIR /omlish

ENTRYPOINT [
  "dumb-init",
  "--"
]

CMD [
  "sh",
  "-c",
  "echo \"Ready\" && sleep infinity"
]
