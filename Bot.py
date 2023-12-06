from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
from config import TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, 'Привет')
    
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler(["start","hello"], start))
app.run_polling()