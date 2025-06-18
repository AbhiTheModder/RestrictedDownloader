# This Module is a part of MoonUserbot and is used here for example
import math
import time
import os
import asyncio

from pyrogram import Client, errors, types, enums, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant, FloodWait, MessageNotModified
from pyrogram.errors import ChatForwardsRestricted


API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

app = Client(
  "rdl_bot",
  api_id=API_ID,
  api_hash=API_HASH,
  session_string=STRING_SESSION,
  device_model=f"RestrictedDL @ {gitrepo.head.commit.hexsha[:7]}",
  system_version=platform.version() + " " + platform.machine()
)

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

@app.on_message(filters.command("rdl", "!) & filters.me)
async def dl(client: Client, message: Message):
    # Extract command arguments
    args = message.command[1:]

    # Check if the required arguments are provided
    if len(args) < 2:
        await message.edit_text(
            "Kindly use `.rdl channel_link message_id [number_of_messages]`"
        )
        return

    chat_id = message.chat.id
    c_time = time.time()
    ch_gp_link = args[0]
    selected_id = int(args[1])
    num_messages = int(args[2]) if len(args) > 2 else 1

    try:
        # Join the chat if not already a participant
        await client.join_chat(ch_gp_link)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        await message.edit_text(format_exc(e))
        return

    try:
        # Get the chat object
        chat = await client.get_chat(ch_gp_link)
        from_chat = chat.id

        # Download and re-upload the specified number of messages
        for _ in range(num_messages):
            ms = await message.edit_text(f"Working on message {selected_id}...")
            selected_message = await client.get_messages(from_chat, selected_id)
            file_text = selected_message.caption

            try:
                # Try to download the media
                file = await client.download_media(
                    selected_message,
                    progress=progress,
                    progress_args=(ms, c_time, f"`Trying to download...`"),
                )
                await client.send_document(
                    chat_id,
                    file,
                    caption=file_text,
                    progress=progress,
                    progress_args=(ms, c_time, f"`Uploading...`"),
                )
                os.remove(file)
            except ValueError:
                # If downloading is restricted, try to copy the message
                await client.copy_message(chat_id, from_chat, selected_id)
            except ChatForwardsRestricted:
                # If downloading is restricted, try to copy the message
                pass

            selected_id += 1

        await ms.delete()
    except Exception as e:
        await message.edit_text(format_exc(e))

app.run()
