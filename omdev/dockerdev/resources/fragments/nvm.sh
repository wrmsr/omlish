set -ex ;

NVM_VERSION=$(
  curl -fsSL -o /dev/null -w '%{url_effective}' 'https://github.com/nvm-sh/nvm/releases/latest' |
  sed 's#.*\/tag/##'
) ;

curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh" | bash ;

export NVM_DIR="$HOME/.nvm" ;
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" ;

for NV in ${NVM_VERSIONS} ; do
  nvm install "$NV" ;
done ;
