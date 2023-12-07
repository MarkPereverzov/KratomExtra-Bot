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
    "UA":["Maeng da БІЛИЙ","Maeng da ЗЕЛЕНИЙ","Maeng da ЧЕРВОНИЙ","Тайський зелений","Борнео червоний","Білий Слон","Шива","White Honey","Богиня Калі","Golden Dragon"]
}
gramms_list = ["10","25","50","100","1000"]
choose_type_list = ["Розсипний","Капсули","Концентрат","Пробний набір"]
menu_list = ["Мої замовлення","Зробити замовлення","Звернутись за допомогою"]

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

ORDER_CORRECT,TEA,HELP,MYORDER,CHECK,TYPE,ORDER,VARIETY, GRAMMS, COUNT,PACKAGE = range(11)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([menu_list],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
    await context.bot.send_message(update.effective_chat.id, 'Привет',reply_markup=reply_markup)
    return CHECK

async def check_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    option = update.message.text
    if option == menu_list[0]:
        return MYORDER
    elif option == menu_list[1]:
        await choose_type(update,context)
        return TEA
    elif option == menu_list[2]:
        return HELP

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Розсипний","Капсули"],["Концентрат","Пробний набір"]],one_time_keyboard=True,resize_keyboard=True)
    await context.bot.send_message(update.effective_chat.id, 'Оберіть форму',reply_markup=reply_markup)
    return TEA

async def choose_tea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type = update.message.text
    context.user_data["type"] = type
    logger.info("%s TYPE", type)
    options_matrix = [
        ["Maeng da БІЛИЙ","Maeng da ЗЕЛЕНИЙ"],
        ["Maeng da ЧЕРВОНИЙ","Тайський зелений"],
        ["Борнео червоний","Білий Слон"],
        ["Шива","White Honey"],
        ["Богиня Калі","Golden Dragon"]
    ]
    reply_markup = ReplyKeyboardMarkup(options_matrix,one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,text='Выберете сорт',reply_markup=reply_markup)
    return VARIETY

async def variety_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options_matrix = [["10","25"],["50","100"],["1000"]]
    reply_markup = ReplyKeyboardMarkup(options_matrix,one_time_keyboard=True,resize_keyboard=True)
    user = update.message.from_user
    variety = update.message.text
    context.user_data["variety"] = variety
    logger.info("%s selected variety : %s", user.first_name, variety)
    await update.message.reply_text(
        "Укажите к-во грамм",
        reply_markup=reply_markup,
    )
    return GRAMMS

async def gramms_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    gramms = update.message.text
    context.user_data["gramms"] = gramms
    logger.info("%s selected %s gramms", user.first_name, gramms)
    await update.message.reply_text(
        "Укажите к-во пакетиков",
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
    reply_markup = ReplyKeyboardMarkup([menu_list],one_time_keyboard=True,resize_keyboard=True)
    if update.message.text == "Так":
        await update.message.reply_text(
        "Дякуємо за замовлення",
        reply_markup=reply_markup
        )
        return ConversationHandler.END
    else:
        choose_type(update,context)
        return TEA

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, 'Замовлення призупинено')
                                   
app = ApplicationBuilder().token(TOKEN).build()
#app.add_handler(CommandHandler(["start","hello"], start))
#app.add_handler(CommandHandler(["order","make_order"], make_order))
app.add_handler(ConversationHandler(
        entry_points=[CommandHandler(["start","hello"], start)],
        states={
            CHECK: [ConversationHandler(
                entry_points=[MessageHandler(filters.Regex(gen_regex(menu_list)),check_menu)],
                states={
                    #MYORDER: [MessageHandler(filters.TEXT),]
                    TEA: [ConversationHandler(
                        entry_points=[MessageHandler(filters.TEXT,choose_tea)],
                        states={
                            #TEA: [MessageHandler(filters.Regex(gen_regex(choose_type_list)),choose_type)],
                            VARIETY: [MessageHandler(filters.Regex(gen_regex(variety_dict["UA"])), variety_select)],
                            GRAMMS: [MessageHandler(filters.Regex(gen_regex(gramms_list)), gramms_select)],
                            PACKAGE: [MessageHandler(filters.Regex("^[0-9]+$"),package_select)],
                            ORDER_CORRECT:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),is_oreder_correct)]
                        },
                        fallbacks=[CommandHandler("cancel", cancel)],
                        )],
                },
                fallbacks=[CommandHandler("cancel", cancel)],
                )], 
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
app.run_polling()