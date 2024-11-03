from fastapi import FastAPI, Request
import telebot
from bot import bot

app = FastAPI()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the bot!")

@app.post("/webhook")
async def webhook(request: Request):
    update = request.json()
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return {"status": "ok"}

@app.get("/")
async def read_root():
    return {"message": "Hello, this is your Telegram bot!"}
