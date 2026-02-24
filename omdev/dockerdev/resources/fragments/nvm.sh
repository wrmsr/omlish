set -ex ;

curl -o- 'https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh' | bash ;

export NVM_DIR="$HOME/.nvm" ;
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" ;

for NV in ${NVM_VERSIONS} ; do
  nvm install "$NV" ;
done
