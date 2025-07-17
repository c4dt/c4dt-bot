import asyncio
from dotenv import load_dotenv
# from agno.models.lmstudio import LMStudio
# from agno.models.openai import OpenAIChat
# from agno.models.openai.like import OpenAILike
# from agno.models.anthropic import Claude
import os
import simplematrixbotlib as botlib
from nio import RoomMessageText

from agent import answer_message, set_logger
from common import ProgressLogger, data_dir

load_dotenv()
matrix_home = os.environ.get("MATRIX_HOME")
matrix_login = os.environ.get("MATRIX_LOGIN")
matrix_pass = os.environ.get("MATRIX_PASS")

if matrix_home == None or matrix_login == None or matrix_pass == None:
    print("Please export MATRIX_HOME, MATRIX_LOGIN, and MATRIX_PASS, and then run the script again")
    os.exit(1)

config = botlib.Config()
config.store_path = f"{data_dir}/store"
config.encryption_enabled = True  # Automatically enabled by installing encryption support
config.emoji_verify = True
config.ignore_unverified_devices = True

creds = botlib.Creds(matrix_home, matrix_login, matrix_pass,
                     session_stored_file=f"{data_dir}/session.txt")
bot = botlib.Bot(creds, config)
PREFIX = '!'

class MatrixLogger(ProgressLogger):
    def __init__(self, room) -> None:
        self.room = room
    
    async def msg(self, message: str) -> None:
        print(self.room, message)
        await bot.api.send_text_message(self.room.room_id, message)
        
    async def log(self, message: str) -> None:
        await self.msg(f"* {message}")
    
    async def debug(self, message: str) -> None:
        await self.msg(f"    - {message}")
    
    async def trace(self, message: str) -> None:
        await self.msg(f"        . {message}")
    
    async def error(self, message: str) -> None:
        await self.msg(f"Error: {message}")

    async def panic(self, message: str) -> None:
        await self.msg(f"PANIC: {message}")

@bot.listener.on_message_event
async def echo(room, message: RoomMessageText):
    match = botlib.MessageMatch(room, message, bot, PREFIX)
    
    if match.is_not_from_this_bot():
        set_logger(MatrixLogger(room))
        answer = await answer_message(message.sender, message.body)
        await bot.api.send_markdown_message(room.room_id, answer)

bot.run()
