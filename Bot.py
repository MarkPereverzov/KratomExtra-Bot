from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, ApplicationBuilder,ConversationHandler, MessageHandler,filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import sqlite3
import logging
from bottoken import TOKEN
from classes import User
from dbwrapper import Dbwrapper

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

variety_dict = {
    "UA":["🌱 Maeng da Білий", "🌱 Maeng da Зелений", "🌱 Maeng da Червоний", "🌱 Тайський зелений","🌱 Борнео червоний", "🌱 Білий Слон","🌱 Шива", "🌱 White Honey", "🌱 Богиня Калі", "🌱 Golden Dragon"]
}
start_reply_markup = ReplyKeyboardMarkup([["📋 Мої замовлення", "📝 Зробити замовлення",], ["📃 Асортимент", "🗣️ Звернутися за допомогою",]],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
gramms_list = ["10 г", "25 г", "50 г", "100 г", "1 кг"]
choose_type_list = ["Розсипний","Капсули","Концентрат","Пробний набір"]
menu_list = ["📋 Мої замовлення", "📝 Зробити замовлення","📃 Асортимент", "🗣️ Звернутися за допомогою"]
local_or_delivery_list = ["Самовивіз", "Доставка"]
post_type_list= ["Почтомат","Відділення"]
contact_info = "Ви можете забрати своє замовлення за адресою: Вул. 12 Квітня, будинок 3"

db = Dbwrapper.Dbwrapper("D:\\KratomUkraine-Bot\\data.db")

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

LOCALORDELIVERY,ORDER_CORRECT,TEA,HELP,MYORDER,CHECK,TYPE,ORDER,VARIETY, GRAMMS, COUNT,PACKAGE, ASSORTMENT,PERSONAL_INFO,PERSONAL_SURNAME,PERSONAL_PHONE,PERSONAL_CITY,PERSONAL_POST_TYPE,PERSONAL_POST_TYPE_CHOOSE,PERSONAL_INFO_CORRECT,PERSONAL_POST_NUMBER = range(21)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, '👋 Вас вітає Kratom Ukraine телеграм бот.\nТут ви можете оформити онлайн замовлення або дізнатися детальніше про наш чай 🌱',reply_markup=start_reply_markup)
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
        "Вага: "+context.user_data["gramms"] + "\n"+
        "Кількість упаковок: "+context.user_data["package"] + "\n"+
        "Все вказано вірно ?",
        reply_markup=reply_markup,
    )
    return ORDER_CORRECT

async def is_oreder_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Так":
        #Проверить есть ли данные в базе
        await update.message.reply_text("📦 Оберіть зручний для вас вид доставки\n\n🚶 Самовивіз\nВи маєте можливість особисто забрати замовлення у зручний для Вас час у проміжок часу (11:00 - 18:00).\n\n🚚 Доставка поштою\nВаше замовлення буде надіслано протягом робочого дня за тарифами Нової Пошти.",
            reply_markup=ReplyKeyboardMarkup([local_or_delivery_list],one_time_keyboard=True,input_field_placeholder="",resize_keyboard=True)
        )
        return LOCALORDELIVERY
    else:
        #await choose_type(update,context)
        return await choose_type(update,context) 
    
async def local_or_delivery(update: Update,context: ContextTypes.DEFAULT_TYPE):
    lod = update.message.text
    if(lod == local_or_delivery_list[0]):
        return await local(update,context)
    else:
        return await personal_info_name(update,context)

async def local(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        contact_info,
        reply_markup=start_reply_markup
    )
    return CHECK

async def personal_info_name(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вкажіть ваше ім'я", reply_markup=ReplyKeyboardRemove())
    return PERSONAL_SURNAME

async def personal_info_surname(update: Update,context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data["name"] = name
    await update.message.reply_text("Вкажіть ваше прізвище")
    return PERSONAL_PHONE

async def personal_info_phone(update: Update,context: ContextTypes.DEFAULT_TYPE):
    surname = update.message.text
    context.user_data["surname"] = surname
    await update.message.reply_text("Вкажіть ваш номер телефону")
    return PERSONAL_CITY

async def personal_info_city(update: Update,context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    context.user_data["phone"] = phone
    await update.message.reply_text("Вкажіть ваше місто")
    return PERSONAL_POST_TYPE

async def personal_info_post_type(update: Update,context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([post_type_list],resize_keyboard=True)
    city = update.message.text
    context.user_data["city"] = city
    await update.message.reply_text("Оберіть Почтомат або Відділення",reply_markup=reply_markup)
    return PERSONAL_POST_TYPE_CHOOSE
    
async def personal_info_post_type_choose(update: Update,context: ContextTypes.DEFAULT_TYPE):
    post_type = update.message.text
    context.user_data["post_type"] = post_type
    await update.message.reply_text(f'Введіть номер {"почтомату" if post_type == post_type_list[0] else "відділення"} (Тільки число)',reply_markup=ReplyKeyboardRemove())
    return PERSONAL_POST_NUMBER

async def personal_info_post_number(update: Update,context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Так","Ні"]],one_time_keyboard=True,resize_keyboard=True)
    post_number = update.message.text
    userid = update.message.from_user.id
    context.user_data["post_number"] = post_number
    user = User.User(userid,context.user_data["name"],context.user_data["surname"],context.user_data["phone"],context.user_data["city"],context.user_data["post_type"],post_number)
    await update.message.reply_text(
        f"userid: {userid}\n{user}\nВсе вказано вірно ?",
        reply_markup=reply_markup,
    )
    return PERSONAL_INFO_CORRECT

async def is_personal_info_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Так":
        print(db.getUser({"ID":"1"}))
        #Проверить есть ли данные в базе
        await update.message.reply_text("Щиро дякуємо за замовлення !",
            reply_markup=start_reply_markup)
        return CHECK
    else:
        return await personal_info_name(update,context) 

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
            ORDER_CORRECT:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),is_oreder_correct)],
            LOCALORDELIVERY:[MessageHandler(filters.Regex(gen_regex(local_or_delivery_list)),local_or_delivery)],
            PERSONAL_INFO:[MessageHandler(filters.TEXT,personal_info_name)],
            PERSONAL_SURNAME:[MessageHandler(filters.TEXT,personal_info_surname)],
            PERSONAL_PHONE:[MessageHandler(filters.TEXT,personal_info_phone)],            
            PERSONAL_CITY:[MessageHandler(filters.TEXT,personal_info_city)],
            PERSONAL_POST_TYPE:[MessageHandler(filters.TEXT,personal_info_post_type)],
            PERSONAL_POST_TYPE_CHOOSE:[MessageHandler(filters.Regex(gen_regex(post_type_list)),personal_info_post_type_choose)],
            PERSONAL_POST_NUMBER:[MessageHandler(filters.Regex("^[0-9]+$"),personal_info_post_number)],
            PERSONAL_INFO_CORRECT:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),is_personal_info_correct)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
app.run_polling()