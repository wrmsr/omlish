set -ex ;

curl -fsSL https://rbenv.org/install.sh | bash ;

for RV in ${RBENV_VERSIONS}; do
  bash -c 'eval "$(~/.rbenv/bin/rbenv init - --no-rehash bash)" && rbenv install -L | grep -F "$1." | grep -E "^[0-9]+\.[0-9]+\.[0-9]+$" | sort -V | tail -n1 | xargs rbenv install' bash "$RV" ;
done ;
