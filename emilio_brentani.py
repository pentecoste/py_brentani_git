from pyrogram import Client, filters
import config

app = Client("Bot Name", bot_token = config.API_TOKEN)

app.run()
