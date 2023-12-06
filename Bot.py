from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, ApplicationBuilder,ConversationHandler, MessageHandler,filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import sqlite3
import logging
from config import TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

ORDER,VARIETY, GRAMMS, COUNT = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Замовлення"]],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
    await context.bot.send_message(update.effective_chat.id, 'Привет',reply_markup=reply_markup)
    return ORDER

async def make_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Кали","Шива"]],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,text='Выберете сорт',reply_markup=reply_markup)
    return VARIETY
async def variety_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    variety = update.message.text
    logger.info("%s selected variety : %s", user.first_name, variety)
    await update.message.reply_text(
        "Укажите к-во грамм",
        reply_markup=ReplyKeyboardRemove(),
    )
    return GRAMMS
async def gramms_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Замовлення"]],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
    user = update.message.from_user
    gramms = update.message.text
    logger.info("%s selected %s gramms", user.first_name, gramms)
    await update.message.reply_text(
        "Спасибо за заказ",
        reply_markup=reply_markup,
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, 'Замовлення призупинено')
                                   
app = ApplicationBuilder().token(TOKEN).build()
#app.add_handler(CommandHandler(["start","hello"], start))
#app.add_handler(CommandHandler(["order","make_order"], make_order))
app.add_handler(ConversationHandler(
        entry_points=[CommandHandler(["start","hello"], start),MessageHandler(filters.Regex("^(Замовлення)$"),make_order)],
        states={
            ORDER: [MessageHandler(filters.TEXT,make_order)], #Regex("^(Замовлення)$"
            VARIETY: [MessageHandler(filters.Regex("^(Кали|Шива)$"), variety_select)],
            GRAMMS: [MessageHandler(filters.TEXT, gramms_select)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
app.run_polling()