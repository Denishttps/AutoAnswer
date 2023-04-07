from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from settings.DB import UserDB
from settings.blackdb import BlackListDB
from settings.config import help_str
from run import keep_alive
import logging

api_id = api_id
api_hash = 'api_hash'
logging.basicConfig(level=logging.INFO)

bot = Client("my_bot", api_id=api_id, api_hash=api_hash)

@bot.on_message(filters.me & filters.command(commands=["add", "добавить", "доб"], prefixes=[".", "!", "/"], case_sensitive=True))
async def add_word(client, msg):
  try:
    message_text = msg.text
    message_lines = message_text.split('\n', maxsplit=1)
    first_arg = message_lines[0].split(' ', maxsplit=1)[1].strip().lower()
    second_arg = message_lines[1]
    try:
      with UserDB() as db:
        db.add_word(word=first_arg, answer=second_arg)
        await msg.edit_text("Готово!")
    except:
      await msg.edit_text("Такое слово/фраза уже есть, для того чтобы сменить ответ удали и добавь сначала.")
  except IndexError:
    await msg.edit_text("Недостаточно аргументов, или они не правильно указаны!\nПример:\n.add Слово, или фраза\nОтветное сообщение")

@bot.on_message(filters.me & filters.command(commands=["answers", "ответы", "words", "слова", "фразы"], prefixes=[".", "!", "/"], case_sensitive=True))
async def answers(client, msg):
  with UserDB() as db:
    get = db.get_all_words()
    f_str = "" 
    for item in get:
      f_str += f"{item[0]}: {item[1]}\n{item[2]}\n\n"
    await msg.edit_text("Все слова/фразы:\n" + f_str)

@bot.on_message(filters.me & filters.command(commands=["help", "помощь"], prefixes=[".", "!", "/"], case_sensitive=True))
async def help_bot(client, msg):
  await msg.edit_text(help_str)
  
  
@bot.on_message(filters.me & filters.command(commands=["del", "удалить"], prefixes=[".", "!", "/"], case_sensitive=True))
async def del_word(client, msg):
  try:
    text = msg.text.lower().split(" ", maxsplit=1)[1]
    with UserDB() as db:
      if text.isnumeric():
        db.del_word(id=int(text))
      else:
        db.del_word(word=text)
      await msg.edit_text("Готово! Слово успешно удалено.")
  except IndexError:
    await msg.edit_text("Недостаточно аргументов! Введи номер, слово/фразу которую хочешь удалить.")

@bot.on_message(filters.me & filters.command(commands=["off", "выключить", "выкл"], prefixes=[".", "!", "/"], case_sensitive=True))
async def off(client, msg):
  with open("off_on.txt") as file:
    if file.read():
      with open("off_on.txt", "w") as f:
        f.write("")
        await msg.edit_text("Готово! Автоответчик выключен")
    else:
      await msg.edit_text("Автоответчик уже был выключен!")

@bot.on_message(filters.me & filters.command(commands=["on", "включить", "вкл"], prefixes=[".", "!", "/"], case_sensitive=True))
async def on(client, msg):
  with open("off_on.txt") as file:
    if not file.read():
      with open("off_on.txt", "w") as f:
        f.write("content")
        await msg.edit_text("Готово! Автоответчик включен")
    else:
      await msg.edit_text("Автоответчик уже был включен!")


@bot.on_message(filters.me & filters.command(commands=["bl"], prefixes=[".", "!", "/"], case_sensitive=True))
async def black_list(client, msg):
    with BlackListDB() as db:
      get = db.get_all_users()
      answer = "Чёрный список:\n"
      for i in get:
        answer += str(i[0]) + ": <a href='tg://user?id='" + str(i[1]) + ">"+str(i[2])+"</a>\nid: <code>"+str(i[1])+"</code>\nUser: @" + str(i[3]) + "\n\n"
      await msg.edit_text(text=answer, parse_mode=ParseMode.HTML)

@bot.on_message(filters.me & filters.command(commands=["addbl"], prefixes=[".", "!", "/"], case_sensitive=True))
async def black_list12(client, msg):
  with BlackListDB() as db:
    try:
      text = msg.text.split(" ", maxsplit=1)[1]
      if text.isnumeric():
        get_user = await bot.get_users(int(text.strip()))
      else:
        get_user = await bot.get_users(str(text.strip()))
      db.add_user(user_id=get_user.id, first_name=get_user.first_name, username=get_user.username)
      await msg.edit_text("Готово! Пользователь добавлен в чёрный список.")
    except:
      await msg.edit_text("Произошла ошибка :(, или пользователь уже в чёрном списке")

@bot.on_message(filters.me & filters.command(commands=["delbl"], prefixes=[".", "!", "/"], case_sensitive=True))
async def del_black_list(client, msg):
  with BlackListDB() as db:
    try:
      text = msg.text.split(" ", maxsplit=1)[1]
      db.del_user(text)
      await msg.edit_text("Готово! Пользователь удалён в чёрный список.")
    except:
      await msg.edit_text("Произошла ошибка :(")

@bot.on_message(filters.me & filters.command(commands=["id", "ид"], prefixes=[".", "!", "/"], case_sensitive=True))
async def id(client, msg):
  reply = msg.reply_to_message
  if reply:
    await msg.edit_text(f"🆔 пользователя равен <code>@{reply.from_user.id}</code>")
  else:
    if len(msg.text.split(" ", maxsplit=1)) > 1:
      get_user = await bot.get_users(msg.text.split(" ", maxsplit=1)[1])
      await msg.edit_text(f"🆔 пользователя равен <code>@{get_user.id}</code>")
    else:
      await msg.edit_text(f"🆔 пользователя равен <code>@{msg.from_user.id}</code>")

  
@bot.on_edited_message(filters.private & ~filters.me)
@bot.on_message(filters.private & ~filters.me)
async def respond_to_keywords(client, message):
  with open("off_on.txt") as f:
    on = f.read()
    if on:
      with BlackListDB() as black_list:
        if black_list.get_user(user_id=message.from_user.id):
          text = message.text.lower()
          with UserDB() as db:
            word = db.get_all_words()
            for i in word:
              if i[1] in text:
                await bot.send_message(message.chat.id, i[2])
                return True


if __name__ == "__main__":
  keep_alive()
  bot.run()
