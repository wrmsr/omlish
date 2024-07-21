"""
curl \
    -H 'Content-Type: application/json' \
    "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d "{\"chat_id\":\"$TELEGRAM_CHAT_ID\",\"text\":\"hi\"}"
"""
import asyncio

from ..secrets import load_secrets

import telegram


async def _a_main():
    token = load_secrets()['telegram_token']

    bot = telegram.Bot(token)
    async with bot:
        print(await bot.get_me())

        updates = list(await bot.get_updates())
        print(updates)


if __name__ == '__main__':
    asyncio.run(_a_main())
