from dotenv import load_dotenv
# from agno.models.lmstudio import LMStudio
# from agno.models.openai import OpenAIChat
# from agno.models.openai.like import OpenAILike
# from agno.models.anthropic import Claude
import os
import simplematrixbotlib as botlib

load_dotenv()
matrix_home = os.environ.get("MATRIX_HOME")
matrix_login = os.environ.get("MATRIX_LOGIN")
matrix_pass = os.environ.get("MATRIX_PASS")

if matrix_home == None or matrix_login == None or matrix_pass == None:
    print("Please export MATRIX_HOME, MATRIX_LOGIN, and MATRIX_PASS, and then run the script again")
    os.exit(1)

config = botlib.Config()
config.store_path = "data/store"
config.encryption_enabled = True  # Automatically enabled by installing encryption support
config.emoji_verify = True
config.ignore_unverified_devices = True

creds = botlib.Creds(matrix_home, matrix_login, matrix_pass)
bot = botlib.Bot(creds, config)
PREFIX = '!'


@bot.listener.on_message_event
async def echo(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)
    
    if match.is_not_from_this_bot():
        print(room, message)

    if match.is_not_from_this_bot()\
            and match.prefix()\
            and match.command("echo"):

        await bot.api.send_text_message(room.room_id,
                                        " ".join(arg for arg in match.args()))


bot.run()
