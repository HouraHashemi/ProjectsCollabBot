import asyncio
import telegram
import statics
import os

import django
from django.conf import settings
from asgiref.sync import sync_to_async
from django.utils import timezone

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from Auction.models import Art, Collector, Bid


async def broadcast_massage(bot):
    all_collectors = Collector.objects.all()
    message = statics.MESSAGES['START']['PUBLIC_ANNOUNCEMENT']
    for collector in all_collectors:
        await bot.send_message(chat_id=collector.chat_id, text=message, parse_mode='Markdown')
    
async def main():
    TOKEN = '6659772243:AAFYrd7iRYDNFaaZJKePSl46bRfIFvbVjXA'

    #That is the easiest way to initiate and send a message.
    bot = telegram.Bot(TOKEN)    
    await broadcast_massage(bot)

if __name__ == '__main__':
    asyncio.run(main())