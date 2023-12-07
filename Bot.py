from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, ApplicationBuilder,ConversationHandler, MessageHandler,filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import sqlite3
import logging
from config import TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

variety_dict = {
    "UA":["Maeng da Білий", "Maeng da Зелений", "Maeng da Червоний", "Тайський зелений", "Борнео червоний", "Білий Слон", "Шива", "White Honey", "Богиня Калі", "Golden Dragon"]
}
gramms_list = ["10г","25г","50г","100г","1кг"]

def gen_regex(list):
    st = "^("
    first = True
    for variety in list:
        if first:
            st+=variety
            first = False
        else:
            st+=f"|{variety}"
    st += ")$"
    return st

ORDER,VARIETY, GRAMMS, COUNT,PACKAGE = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["📋 Мої замовлення", "📝 Зробити замовлення",], ["📃 Асортимент", "🗣️ Звернутися за допомогою",]],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
    await context.bot.send_message(update.effective_chat.id, 'Вас вітає Kratom Ukraine телеграм бот 👋\nТут ви можете оформити онлайн замовлення або дізнатися детальніше про наш чай 🌱',reply_markup=reply_markup)
    return ORDER

async def make_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options_matrix = [
        ["🌱 Maeng da Білий", "🌱 Maeng da Зелений"],
        ["🌱 Maeng da Червоний", "🌱 Тайський зелений"],
        ["🌱 Борнео червоний", "🌱 Білий Слон"],
        ["🌱 Шива", "🌱 White Honey"],
        ["🌱 Богиня Калі", "🌱 Golden Dragon"],
    ]
    reply_markup = ReplyKeyboardMarkup(options_matrix,one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,text='Оберіть сорт',reply_markup=reply_markup)
    return VARIETY

async def variety_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options_matrix = [["10г","25г"],["50г","100г"],["1кг"]]
    reply_markup = ReplyKeyboardMarkup(options_matrix,one_time_keyboard=True,resize_keyboard=True)
    user = update.message.from_user
    variety = update.message.text
    if variety == "Пробний набір":
        return PACKAGE
    logger.info("%s selected variety : %s", user.first_name, variety)
    await update.message.reply_text(
        "Оберіть вагу упаковки",
        reply_markup=reply_markup,
    )
    return GRAMMS

async def gramms_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    gramms = update.message.text
    logger.info("%s selected %s gramms", user.first_name, gramms)
    await update.message.reply_text(
        "Вкажіть кількість упаковок",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PACKAGE
    
async def package_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Замовлення"]],one_time_keyboard=True,resize_keyboard=True)
    package = update.message.text
    user = update.message.from_user
    logger.info("%s selected %s package", user.first_name, package)
    await update.message.reply_text(
        "Щиро дякуємо за замовлення",
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
            VARIETY: [MessageHandler(filters.Regex(gen_regex(variety_dict["UA"])), variety_select)],
            GRAMMS: [MessageHandler(filters.Regex(gen_regex(gramms_list)), gramms_select)],
            PACKAGE: [MessageHandler(filters.Regex("^[0-9]+$"),package_select)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
app.run_polling()