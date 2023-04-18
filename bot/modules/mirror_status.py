from psutil import cpu_percent, virtual_memory, disk_usage
from time import time
from threading import Thread
from telegram.ext import CommandHandler, CallbackQueryHandler

from bot import dispatcher, status_reply_dict, status_reply_dict_lock, download_dict, download_dict_lock, botStartTime, DOWNLOAD_DIR, Interval, DOWNLOAD_STATUS_UPDATE_INTERVAL
from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage, auto_delete_message, sendStatusMessage, update_all_messages
from bot.helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time, turn, setInterval
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands


def mirror_status(update, context):
    with download_dict_lock:
        count = len(download_dict)
    if count == 0:
        currentTime = get_readable_time(time() - botStartTime)
        free = get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)
        message = '🌺 Clear the field and start the game\n⊱✤┅┅┅●( 𝐀ɴɢᴇʟ✘𝐎ᴘ 𝐋𝐨𝐋 )●┅┅┅✤⊰'
        message += f"\n<b>◎ Cᴘᴜ:</b> {cpu_percent()}% | <b>◎ Fʀᴇᴇ:</b> {free}" \
                   f"\n<b>◎ Rᴀᴍ:</b> {virtual_memory().percent}% | <b>◎ Uᴘᴛɪᴍᴇ:</b> {currentTime}"
        reply_message = sendMessage(message, context.bot, update.message)
        Thread(target=auto_delete_message, args=(context.bot, update.message, reply_message)).start()
    else:
        index = update.effective_chat.id
        with status_reply_dict_lock:
            if index in status_reply_dict:
                deleteMessage(context.bot, status_reply_dict[index][0])
                del status_reply_dict[index]
            try:
                if Interval:
                    Interval[0].cancel()
                    Interval.clear()
            except:
                pass
            finally:
                Interval.append(setInterval(DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages))
        sendStatusMessage(update.message, context.bot)
        deleteMessage(context.bot, update.message)

def status_pages(update, context):
    query = update.callback_query
    data = query.data
    data = data.split()
    query.answer()
    done = turn(data)
    if done:
        update_all_messages(True)
    else:
        query.message.delete()


mirror_status_handler = CommandHandler(BotCommands.StatusCommand, mirror_status,
                                       filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)

status_pages_handler = CallbackQueryHandler(status_pages, pattern="status", run_async=True)
dispatcher.add_handler(mirror_status_handler)
dispatcher.add_handler(status_pages_handler)
