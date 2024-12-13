"""
Using no external libraries, write a python program that acts as both a cli tool and an on-demand background service -
use the builtin simple http.server to make a server that just has a /time endpoint that returns the current time, but
make it so the server starts in the background automatically (if it isn't already running) when the user uses its cli.

Only one instance of the server should run at any given time, and the server should linger for 10 minutes to serve
additional requests without having to start a new instance. The server should run in an external process from the cli
that's starting it, and that process should outlive the cli process. Use a double-fork approach to daemonize the server
process, but use a pidfile to ensure it only does so when not already running.

The CLI should have a 'time' command that will call the /time endpoint on the server and print the result, starting the
server if necessary.

==

uv run --with mlx-lm \
  mlx_lm.generate \
  --model mlx-community/Qwen2.5-Coder-32B-Instruct-8bit \
  --model mlx-community/Mixtral-8x7B-Instruct-v0.1 \
  --model mlx-community/Llama-3.3-70B-Instruct-8bit \
  --max-tokens 999999 \
  --prompt
"""
