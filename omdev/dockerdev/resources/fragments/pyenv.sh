set -ex ;

git clone 'https://github.com/pyenv/pyenv' ~/.pyenv ;

for V in ${PYENV_VERSIONS} ; do
  PYTHON_BUILD_CACHE_PATH=~/.pyenv_cache ~/.pyenv/bin/pyenv install -s "$V" ;
done ;
