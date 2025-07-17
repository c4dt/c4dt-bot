# c4dt-bot - get some LLM magic to do weekly picks - Licensed under AGPLv3 or later
# Copyright (C) <2025>  <Linus.Gasser@epfl.ch>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import datetime
from dotenv import load_dotenv
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
        with open(f"{data_dir}/logger.log", "a") as f:
            f.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + message)
            
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
