set -ex ;

GO_VERSION=$(curl -fsSL 'https://go.dev/VERSION?m=text' | head -n1 | sed 's/^go//') ;

curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-$(dpkg --print-architecture).tar.gz" | tar -C "$HOME" -xzf - ;
mv "$HOME/go" "$HOME/.go" ;

echo '\n
export GOROOT="$HOME/.go"\n
export PATH="$GOROOT/bin:$PATH"\n
' >> ~/.bashrc ;
