from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, ApplicationBuilder
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
import sqlite3
from config import TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, 'Привет',reply_markup=GetReplyKeyboardMarkup())

async def add_lector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,text='Send lector name')
    return EXPECT_LECTOR_NAME

def GetReplyKeyboardMarkup():
    return ReplyKeyboardMarkup([["test1","test2"]])

    
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler(["start","hello"], start))
app.run_polling()