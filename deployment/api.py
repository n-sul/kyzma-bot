from fastapi import FastAPI, Request
import telebot
from bot import bot

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Hello, this is your Telegram bot!"}
