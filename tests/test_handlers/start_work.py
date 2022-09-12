from telethon import TelegramClient
import asyncio
api_id = 12093886
api_hash = "f494130046561d51ec849bc660d0934c"
client = TelegramClient('first_test', api_id, api_hash)
client.start()

from telethon.sync import TelegramClient, events

with TelegramClient('name', api_id, api_hash) as client:
   client.send_message(5320843943, '/start')

   @client.on(events.NewMessage(pattern=r'\Привет Михаил.'))
   async def handler(event):
      if event.reply == "Хорошо.Напиши что ты хочешь пообещать":




   client.run_until_disconnected()