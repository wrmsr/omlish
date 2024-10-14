from x.llm.swarm.examples.weather_agent.agents import weather_agent
from x.llm.swarm.repl import run_demo_loop


if __name__ == '__main__':
    run_demo_loop(weather_agent, stream=True)
