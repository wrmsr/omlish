set -ex

export GO_VERSION=1.25.6
curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-$(dpkg --print-architecture).tar.gz" | tar -C "$HOME" -xzf -
mv "$HOME/go" "$HOME/.go"
echo '\n\
export GOROOT="$HOME/.go"\n\
export PATH="$GOROOT/bin:$PATH"\
' >> ~/.bashrc
