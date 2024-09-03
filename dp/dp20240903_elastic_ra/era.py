import os.path
import yaml


with open(os.path.expanduser('~/Dropbox/.dotfiles/secrets.yml')) as f:
    os.environ['TAVILY_API_KEY'] = yaml.safe_load(f)['tavily_api_key']


def _main():
    local_llm = 'llama3'


if __name__ == '__main__':
    _main()
