import random
from gtts import gTTS
import sqlite3
import telebot
from telebot import TeleBot
from telebot import types
import os

token = os.environ.get('TOKEN')
bot: TeleBot = telebot.AsyncTeleBot(str(token))

db = sqlite3.connect('tg-database.db', check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS clans(
    chat_id BIGINT,
    clan_name TEXT,
    creator_id BIGINT
)""")
db.commit()

sql.execute("""CREATE TABLE IF NOT EXISTS users(
    chat_id BIGINT,
    clan_name TEXT,
    user_id BIGINT
)""")
db.commit()

markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn_abilities = types.KeyboardButton('Верификация✅')
markup_menu.add(btn_abilities)

markup_menu_zero = types.ReplyKeyboardRemove()

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        sql.execute(f"SELECT verification FROM verified WHERE id = '{user_id}'")
        if sql.fetchone() is None:
            bot.send_message(message.chat.id, 'Верифицируйтесь', reply_markup=markup_menu)
        else:
            pass


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message.text)
    chat_id = message.chat.id
    if message.chat.type == "group" or message.chat.type == "supergroup":
        if message.text.startswith('!создать '):
            user_id = message.from_user.id
            sql.execute(f"SELECT clan_name FROM users WHERE user_id = '{user_id}' AND chat_id = '{chat_id}'")
            if sql.fetchone() is None:
                message_txt = message.text
                clan_name = message_txt[9:]
                user_id = message.from_user.id
                chat_id = message.chat.id
                sql.execute("SELECT chat_id FROM clans")
                sql.execute(f"INSERT INTO clans VALUES(?, ?, ?)", (chat_id, clan_name, user_id))
                db.commit()
                sql.execute("SELECT chat_id FROM users")
                sql.execute(f"INSERT INTO users VALUES(?, ?, ?)", (chat_id, clan_name, user_id))
                db.commit()
                message_for_finish = ('Клан ' + clan_name + ' успешно создан!')
                bot.send_message(message.chat.id, message_for_finish, reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, 'Вы уже в клане. Покиньте или удалите его',
                                 reply_to_message_id=message.message_id)
        if message.text.startswith('!вступить '):
            message_txt = message.text
            clan_name = str(message_txt[10:])
            user_id = message.from_user.id
            sql.execute(f"SELECT clan_name FROM clans WHERE clan_name = '{clan_name}' AND chat_id = '{chat_id}'")
            if sql.fetchall():
                sql.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
                if sql.fetchone() is None:
                    sql.execute("SELECT chat_id FROM users")
                    sql.execute(f"INSERT INTO users VALUES(?, ?, ?)", (chat_id, clan_name, user_id))
                    db.commit()
                    bot.send_message(message.chat.id, 'Вы успешно вступили в клан',
                                     reply_to_message_id=message.message_id)
                else:
                    bot.send_message(message.chat.id, 'Вы уже состоите в клане',
                                     reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, 'Такого клана нет. Но вы можете его создать!',
                                 reply_to_message_id=message.message_id)
        if message.text == '!удалить клан':
            chat_id = message.chat.id
            user_id = message.from_user.id
            sql.execute(f"SELECT clan_name FROM clans WHERE creator_id = '{user_id}' AND chat_id = '{chat_id}'")
            if sql.fetchone():
                sql.execute(f"SELECT clan_name FROM clans WHERE creator_id = '{user_id}' AND chat_id = '{chat_id}'")
                clan_name = str(sql.fetchone())
                sql.execute(f"DELETE FROM clans WHERE creator_id = '{user_id}' AND chat_id = '{chat_id}'")
                sql.execute(f"DELETE FROM clans WHERE clan_name = ? AND chat_id = ?", (clan_name, chat_id))
                db.commit()
                bot.send_message(message.chat.id, 'Клан удалён',
                                 reply_to_message_id=message.message_id)
                bot.send_sticker(message.chat.id,
                                 "CAACAgIAAxkBAAEB0kxgEZuxK_-2D-yw8hh4Avz_nbB6EAACMgAD6JAuHr6oHAH8GzuzHgQ")
            else:
                bot.send_message(message.chat.id, 'Такого клана нет или вы не являетесь лидером клана',
                                 reply_to_message_id=message.message_id)
        if message.text == '!список кланов':
            list_of_clans = 'Список кланов:'
            for value in sql.execute(f"SELECT clan_name FROM clans WHERE chat_id = '{chat_id}'"):
                list_of_clans += '\n--------------------------'
                list_of_clans += '\n' + str(value[0])
            bot.send_message(message.chat.id, list_of_clans)
        if message.text == 'Привет, ботинок':
            if message.from_user.id == 506368232 or message.from_user.id == 908659572:
                bot.send_message(message.chat.id, 'Здравствуй, создатель. Рад слышать Вас!')
                bot.send_sticker(message.chat.id,
                                 "CAACAgIAAxkBAAEB0kpgEZo-XsmXtvrx553agqiKItzv8gACQQAD8i1rHMdxFPt-CHtWHgQ")
            else:
                bot.send_message(message.chat.id, 'Я тебе не ботинок, кожаный!')
        if message.text.startswith('!насколько я '):
            word = str(message.text[13:])
            percent = random.randint(0, 100)
            result = 'Ты ' + word + ' на ' + str(percent) + '%'
            bot.send_message(message.chat.id, result, reply_to_message_id=message.message_id)
        elif message.text.startswith('!насколько '):
            word = str(message.text[11:])
            percent = random.randint(0, 100)
            result = word + ' на ' + str(percent) + '%'
            bot.send_message(message.chat.id, result, reply_to_message_id=message.message_id)
        if message.text == '!рандом песня':
            number = random.randint(1, 8)
            sql.execute(f"SELECT song FROM lyrics WHERE number = '{number}'")
            song = sql.fetchone()
            bot.send_message(message.chat.id, song)
        if message.text == 'Ботинок, ты тут?':
            if message.from_user.id == 506368232 or message.from_user.id == 908659572:
                bot.send_message(message.chat.id, 'Я тут, повелитель. Рад слышать Вас!',
                                 reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, 'Я тебе не ботинок, кожаный!',
                                 reply_to_message_id=message.message_id)
                numb = random.randint(1, 2)
                if numb == 1:
                    bot.send_sticker(message.chat.id,
                                     "CAACAgIAAxkBAAEB2QABYB7PQz-ux2MizxmNorCZMsvdqmkAAj4AA-iQLh6F0Ov-_i_paR4E")
                else:
                    bot.send_sticker(message.chat.id,
                                     "CAACAgIAAxkBAAEB2QJgHs9jo-pX4wYNUUUpDWesFZ1GBwACXAAD8i1rHEorQ0kIWHuGHgQ")
        if message.text == '!кто я':
            user_id = message.from_user.id
            user_name = str(message.from_user.first_name) + ' '
            if message.from_user.last_name is not None:
                user_name += ' ' + str(message.from_user.last_name)
            sql.execute(f"SELECT verification FROM verified WHERE id = '{user_id}'")
            if sql.fetchone() is None:
                verification = 'нет'
            else:
                verification = 'есть'
            chat_name = message.chat.title
            text = 'Информация' + '\n=============' + '\nИмя - ' + user_name + '\n--------------------------' + '\nID - ' + str(
                user_id) + '\n--------------------------' + '\nЧат - ' + chat_name
            text += '\n=============' + '\nВерификация в боте - ' + verification
            bot.send_message(message.chat.id, text,
                             reply_to_message_id=message.message_id)
        if message.text.startswith('!лорд скажи '):
            print('worked')
            text = message.text[12:]
            speech = gTTS(text= text, lang='ru',slow=False)
            speech.save('speech.ogg')
            voice = open('speech.ogg', 'rb')
            bot.send_voice(message.chat.id, voice)
    else:
        if message.text == 'Верификация✅':
            user_id = message.from_user.id
            sql.execute(f"SELECT id FROM verified WHERE id = '{user_id}'")
            if sql.fetchone() is None:
                sql.execute(f"INSERT INTO verified VALUES(?, ?, ?)", (user_id, 'yes', 'no'))
                db.commit()
                bot.send_message(message.chat.id, 'Вы успешно верифицированы', reply_markup=markup_menu_rpg_start)
            else:
                bot.send_message(message.chat.id, 'Вы уже верифицированы', reply_markup=markup_menu_zero)
        else:
            return chat_id


@bot.message_handler(content_types=['new_chat_members'])
def new_chat_members(message):
    user_name = str(message.from_user.first_name) + ' '
    if message.from_user.last_name is not None:
        user_name += ' ' + str(message.from_user.last_name)
    greeting = 'Добро пожаловать в царство ужасов, ' + str(user_name)
    bot.send_message(message.chat.id, greeting, reply_to_message_id=message.message_id)


@bot.message_handler(content_types=['left_chat_member'])
def new_chat_members(message):
    user_name = str(message.from_user.first_name) + ' '
    if message.from_user.last_name is not None:
        user_name += ' ' + str(message.from_user.last_name)
    farewell = 'Rest In Peace ' + str(user_name)
    bot.send_message(message.chat.id, farewell, reply_to_message_id=message.message_id)


bot.infinity_polling()

# markup_menu_1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
# back_btn = types.KeyboardButton('!Назад!')
# markup_menu_1.add(back_btn)
