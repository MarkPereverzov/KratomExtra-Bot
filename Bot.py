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
    "UA":["🌱 Maeng da Білий", "🌱 Maeng da Зелений", "🌱 Maeng da Червоний", "🌱 Тайський зелений","🌱 Борнео червоний", "🌱 Білий Слон","🌱 Шива", "🌱 White Honey", "🌱 Богиня Калі", "🌱 Golden Dragon"]
}
start_reply_markup = ReplyKeyboardMarkup([["📋 Мої замовлення", "📝 Зробити замовлення",], ["Асортимент", "Звернутися за допомогою",]],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
gramms_list = ["10 г", "25 г", "50 г", "100 г", "1 кг"]
choose_type_list = ["Розсипний", "Капсули", "Концентрат", "📦 Пробний набір"]
menu_list = ["📋 Мої замовлення", "📝 Зробити замовлення", "Асортимент", "Звернутися за допомогою"]
local_or_delivery_list = ["Самовивіз", "Доставка"]

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

LOCALORDELIVERY,ORDER_CORRECT,TEA,HELP,MYORDER,CHECK,TYPE,ORDER,VARIETY, GRAMMS, COUNT,PACKAGE, ASSORTMENT = range(13)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, 'Вас вітає Kratom Ukraine телеграм бот 👋\nТут ви можете оформити онлайн замовлення або дізнатися детальніше про наш чай 🌱',reply_markup=start_reply_markup)
    return CHECK

async def myorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Це список ваших замовлень:",
        reply_markup=start_reply_markup,
    )
    return ConversationHandler.END

async def assortment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ви маєте можливість ознайомитися з асортиментом нашого чаю 🌱",
        reply_markup=start_reply_markup,
    )

async def check_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    option = update.message.text
    if option == menu_list[0]:
        return myorder(update,context)
    elif option == menu_list[1]:
        return await choose_type(update,context)
    elif option == menu_list[2]:
        return assortment(update,context) 

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Розсипний","Капсули"],["Концентрат","Пробний набір"]],one_time_keyboard=True,resize_keyboard=True)
    await context.bot.send_message(update.effective_chat.id, '📦 Оберіть зручну форму пакування',reply_markup=reply_markup)
    return TEA

async def choose_tea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type = update.message.text
    context.user_data["type"] = type
    logger.info("%s TYPE", type)
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
    options_matrix = [["10 г","25 г"],["50 г","100 г"],["1 кг"]]
    reply_markup = ReplyKeyboardMarkup(options_matrix,one_time_keyboard=True,resize_keyboard=True)
    user = update.message.from_user
    variety = update.message.text
    context.user_data["variety"] = variety
    logger.info("%s selected variety : %s", user.first_name, variety)
    await update.message.reply_text(
        "⚖︎ Оберіть вагу упаковки",
        reply_markup=reply_markup,
    )
    return GRAMMS

async def gramms_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    gramms = update.message.text
    context.user_data["gramms"] = gramms
    logger.info("%s selected %s gramms", user.first_name, gramms)
    await update.message.reply_text(
        "Вкажіть кількість упаковок",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PACKAGE
    
async def package_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Так","Ні"]],one_time_keyboard=True,resize_keyboard=True)
    package = update.message.text
    context.user_data["package"] = package
    user = update.message.from_user
    logger.info("%s selected %s package", user.first_name, package)
    await update.message.reply_text(
        "Форма: "+context.user_data["type"] + "\n"+
        "Сорт: "+context.user_data["variety"] + "\n"+
        "Кількість грамм в пакеті: "+context.user_data["gramms"] + "\n"+
        "Кількість упаковок: "+context.user_data["package"] + "\n"+
        "Всё указано верно ?",
        reply_markup=reply_markup,
    )
    return ORDER_CORRECT

async def is_oreder_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Так":
        #Проверить есть ли данные в базе
        await update.message.reply_text(
        "Щиро дякуємо за замовлення!",
        reply_markup=ReplyKeyboardMarkup([local_or_delivery_list])
        )
        return LOCALORDELIVERY
    else:
        #await choose_type(update,context)
        await update.message.reply_text("Меню",
        reply_markup=start_reply_markup
        )
        return CHECK
    
async def local_or_delivery(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оберіть Самовивіз чи Доставка"
    )
    lod = update.message.text
    if(lod == local_or_delivery_list[0]):
        local(update,context)
    else:
        delivery(update,context)

async def local(update: Update,context: ContextTypes.DEFAULT_TYPE):
    return 0

async def delivery(update: Update,context: ContextTypes.DEFAULT_TYPE):
    return 0


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, 'Замовлення призупинено')

app = ApplicationBuilder().token(TOKEN).build()
#app.add_handler(CommandHandler(["start","hello"], start))
#app.add_handler(CommandHandler(["order","make_order"], make_order))
app.add_handler(ConversationHandler(
        entry_points=[CommandHandler(["start","hello"], start),[MessageHandler(filters.Regex(gen_regex(menu_list)),check_menu)]],
        states={
            CHECK: [MessageHandler(filters.Regex(gen_regex(menu_list)),check_menu)],
            TEA: [MessageHandler(filters.TEXT,choose_tea)],
            VARIETY: [MessageHandler(filters.Regex(gen_regex(variety_dict["UA"])), variety_select)],
            GRAMMS: [MessageHandler(filters.Regex(gen_regex(gramms_list)), gramms_select)],
            PACKAGE: [MessageHandler(filters.Regex("^[0-9]+$"),package_select)],
            ORDER_CORRECT:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),is_oreder_correct)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
app.run_polling()