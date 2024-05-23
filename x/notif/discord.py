import discord

from omserv.secrets import load_secrets


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


def _main():
    cfg = load_secrets()

    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(cfg['discord_token'])


if __name__ == '__main__':
    _main()
