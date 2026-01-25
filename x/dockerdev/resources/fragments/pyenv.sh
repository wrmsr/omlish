set -ex ;

git clone 'https://github.com/pyenv/pyenv' /root/.pyenv ;

for V in ${PYENV_VERSIONS} ; do
  PYTHON_BUILD_CACHE_PATH=/root/.pyenv_cache /root/.pyenv/bin/pyenv install -s "$V" ;
done
