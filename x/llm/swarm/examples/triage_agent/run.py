from agents import triage_agent
from x.llm.swarm.repl import run_demo_loop

from x.dp.utils import load_secrets


load_secrets()


if __name__ == '__main__':
    run_demo_loop(triage_agent)
