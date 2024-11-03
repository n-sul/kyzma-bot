import telebot
from telebot import types
import time
import random
from users import users  # Import the users list from users.py
import logging
from dotenv import load_dotenv
from os import getenv

# Get enviromental variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='bot.log',  # Log file name
    level=logging.INFO,   # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

bot = telebot.TeleBot(getenv("BOT_TOKEN"))
invest_button_text = "Взаиморозщеты🦗"

# Define the list of commands
commands = [
    {"command": "start", "description": "Запустить бота"},
    {"command": "help", "description": "Получить помощь"},
    {"command": "kyzma", "description": "Фармить KyzmaCoin"},
    {"command": "video", "description": "Пасхалка"},
    {"command": "dice", "description": "Бросить кубик"},
    {"command": "top", "description": "Топ-10 фармил KyzmaCoin"}
]

def get_commands_list():
    return "\n".join([f"/{cmd['command']} - {cmd['description']}" for cmd in commands])

# Function to create the keyboard menu
def create_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    invest_button = types.KeyboardButton(invest_button_text)
    markup.add(invest_button)
    return markup

# Helper function to find a user in the list
def find_user(user_id):
    for user in users:
        if user['user_id'] == user_id:  # Ensure this matches the new user structure
            return user
    return None

def save_users():
    with open('users.py', 'w') as file:
        file.write("users = " + repr(users))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Поздравляем! Вы подписались на Кузьма Invest.\n\nВоспользуйтесь /help чтобы узнать все доступные команды", reply_markup=create_menu())
    logging.info(f"/start used by {message.from_user.username}.")
    
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.set_my_commands(commands)
    bot.reply_to(message, f"Вот список доступных команд:\n{get_commands_list()}")
    logging.info(f"/help used by {message.from_user.username}.")
    

@bot.message_handler(func=lambda message: message.text == invest_button_text)
def handle_invest(message):
    bot.reply_to(message, invest_button_text)
    print('Message sent!')
    logging.info(f"Vzaimorozschety used by {message.from_user.username}.")

@bot.message_handler(commands=['video'])
def send_video(message):
    with open('video.mp4', 'rb') as video:
        bot.send_video(message.chat.id, video, supports_streaming=True)
    print('Message sent!')
    logging.info(f"/video {message.from_user.username}.")
    

@bot.message_handler(commands=['dice'])
def throw_dice(message):
    try:
        logging.info(f'/dice used by {message.from_user.username}')
        # Split the message into parts
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "Используйте формат: /dice 1-6 ставка")
            return
        
        dice_value = int(parts[1])
        coins = int(parts[2])

        # Validate input
        if dice_value < 1 or dice_value > 6:
            bot.reply_to(message, "Значение кубика должно быть от 1 до 6.")
            return
        if coins <= 0:
            bot.reply_to(message, "Количество монет должно быть положительным.")
            return

        # Get user info
        user_id = message.from_user.id
        user = find_user(user_id)

        if user is None or user['coins'] < coins:
            bot.reply_to(message, "У вас недостаточно монет для этой ставки.")
            return

        # Roll the dice
        dice = bot.send_dice(message.chat.id)
        actual_value = dice.dice.value

        # Calculate the result
        if dice_value == actual_value:
            user['coins'] += coins  # Double the coins if guessed correctly
            bot.reply_to(message, f"Поздравляю! На кубике {actual_value}. У вас теперь {user['coins']} KyzmaCoin.")
            
        else:
            user['coins'] -= coins  # Deduct the coins if guessed incorrectly
            bot.reply_to(message, f"Увы, на кубике {actual_value}. У вас осталось {user['coins']} KyzmaCoin.")

        # Save updated user data
        save_users()  # Call the function to save users to users.py

    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите правильные значения для кубика и монет.")

    

# @bot.message_handler(commands=['donbasik'])
# def send_to_donbasik(message):
#     admin = 1457990992
#     messages = ["ПОЛИКАЙ МОЇ ЯЙКА", "Я АКІМ Я ТЕБЕ ЛЮБЛЮ", "Я АКІМ ЖЕНИСЬ НА МЕНІ"]
#     bot.send_message(admin, random.choice(messages))
#     print(f"Message to {admin} sent!")
#     logging.info(f"/donbasik used by {message.from_user.username}")
    
@bot.message_handler(commands=['kotuleva'])
def denza_faradenza(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "денза фараденза.")
    
@bot.message_handler(commands=['top'])
def show_top_users(message):
    # Sort users by coins in descending order
    sorted_users = sorted(users, key=lambda x: x['coins'], reverse=True)

    # Prepare the top 10 users message
    top_users_message = "Топ-10 пользователей по KyzmaCoin:\n"
    for i, user in enumerate(sorted_users[:10], start=1):
        top_users_message += f"{i}. {user['nickname']} - {user['coins']} KyzmaCoin\n"

    # Handle the case when there are no users
    if not sorted_users:
        top_users_message = "Пока нет пользователей."

    bot.reply_to(message, top_users_message)
    logging.info(f"/top used by {message.from_user.username}.")


@bot.message_handler(commands=['kyzma'])
def kuzma_farm(message):
    user_id = message.from_user.id
    current_time = time.time()  # Get the current time in seconds

    user = find_user(user_id)

    logging.info(f"/kyzma used by {message.from_user.username}")

    if user is None:
        # Add new user with initial values
        new_user = {
            'user_id': user_id,
            'nickname': message.from_user.username,
            'coins': 0,
            'last_farm_time': 0  # Initialize last farm time to 0
        }
        users.append(new_user)
        print("Added new user:", new_user)
        save_users()  # Save users after adding a new user
        user = new_user
    else:
        # Check if at least an hour has passed since the last farming
        if current_time - user['last_farm_time'] < 3600:  # 3600 seconds = 1 hour
            remaining_time = 3600 - (current_time - user['last_farm_time'])
            remaining_minutes = remaining_time // 60
            remaining_seconds = remaining_time % 60
            bot.reply_to(message, f"Вы можете фармить снова через {int(remaining_minutes)} минут и {int(remaining_seconds)} секунд.")
            return

        # It's time to farm
        coins = random.randint(1, 30)
        user['coins'] += coins
        user['last_farm_time'] = current_time  # Update last farm time to now
        bot.reply_to(message, f"Вы заработали {coins} KyzmaCoin! У вас теперь {user['coins']} KyzmaCoin.")
        print(f"User {user['nickname']} farmed {coins} coins. Total: {user['coins']}")
        save_users()  # Save users after farming coins


    
bot.infinity_polling()

