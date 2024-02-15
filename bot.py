import math
import time
import os
import json
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Retrieve the environment variable
sudo_users = os.getenv('SUDO_USER_IDS') # use ```export SUDO_USER_IDS=ID1,ID2,ID3``` to set
# Split the string into a list of strings
sudo_users_list = sudo_users.split(',')

# Convert the list of strings to a list of integers
SUDO_USERS = [int(user_id) for user_id in sudo_users_list]

from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram import Client, errors, types, enums, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant

def time_formatter(milliseconds: int) -> str:
    """Time Formatter"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " day(s), ") if days else "")
        + ((str(hours) + " hour(s), ") if hours else "")
        + ((str(minutes) + " minute(s), ") if minutes else "")
        + ((str(seconds) + " second(s), ") if seconds else "")
        + ((str(milliseconds) + " millisecond(s), ") if milliseconds else "")
    )
    return tmp[:-2]

def humanbytes(size):
    """Convert Bytes To Bytes So That Human Can Read It"""
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"

async def progress(current, total, message, start, type_of_ps, file_name=None):
    """Progress Bar For Showing Progress While Uploading / Downloading File - Normal"""
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        if elapsed_time == 0:
            return
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "{0}{1} {2}%\n".format(
            "".join(["▰" for i in range(math.floor(percentage / 10))]),
            "".join(["▱" for i in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            humanbytes(current), humanbytes(total), time_formatter(estimated_total_time)
        )
        if file_name:
            try:
                await message.edit(
                    "{}\n**File Name:** `{}`\n{}".format(type_of_ps, file_name, tmp, parse_mode=enums.ParseMode.MARKDOWN)
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass
        else:
            try:
                await message.edit("{}\n{}".format(type_of_ps, tmp), parse_mode=enums.ParseMode.MARKDOWN)
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except MessageNotModified:
                pass

app = Client("limitbreaker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    if message.from_user.id not in SUDO_USERS:
        await message.reply("You are not authorized to use this command.")
        return
    else:
        await message.reply("Welcome Back, Which channel you're gonna leech :)")

@app.on_message(filters.command("dl"))
async def dl(client: Client, message: Message):
    chat_id = message.chat.id
    c_time = time.time()
    if message.from_user.id not in SUDO_USERS:
        await message.reply("You are not authorized to use this command.")
        return
    elif message.from_user.id in SUDO_USERS:
        if len(message.command) > 2:
            ms = await message.reply("Working on it...")
            ch_gp_link = message.text.split()[1]
            selected_id = int(message.text.split()[2])
            try:
                raj = await app.get_chat(ch_gp_link)
                from_chat = raj.id
                selected_message = await app.get_messages(raj.id, selected_id)
                file_text = selected_message.caption
                file = await app.download_media(selected_message, progress=progress, progress_args=(ms, c_time, f'`Trying to download...`'))
                await client.send_document(chat_id, file, caption=file_text, progress=progress, progress_args=(ms, c_time, f'`Uploading...`'))
            except ValueError:
                await client.copy_message(chat_id, from_chat, selected_id)
        else:
            await message.reply("Kindly use `/dl channel_link message_id")

app.run()