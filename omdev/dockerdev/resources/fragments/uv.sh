set -ex ;

curl -LsSf 'https://astral.sh/uv/install.sh' | sh ;

for PV in ${UV_PYTHON_VERSIONS} ; do
  bash --login -c "uv python install $PV" ;
done ;
