from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, ApplicationBuilder,ConversationHandler, MessageHandler,filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
import logging
import time
from bottoken import TOKEN
from classes import User,OrderElements,Orders, Kratom, Grade,GradeCost,CostElement
from sqlalchemy.sql.expression import func

SRC_PATH = "D:\\KratomUkraine-Bot\\"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

variety_dict = {
    "UA":["Maeng da Білий", "Maeng da Зелений", "Maeng da Червоний", "Тайський зелений","Борнео червоний", "Білий Слон","Шива", "White Honey", "Богиня Калі", "Golden Dragon"]
}
start_reply_markup = ReplyKeyboardMarkup([["📘 Каталог","🛍️ Кошик"],["📜 Мої замовлення","❓ FAQ","📱 Контакти" ]],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
gramms_list = ["10 г", "25 г", "50 г", "100 г", "1 кг"]
choose_type_list = ["Розсипний","Капсули","Концентрат","Пробний набір"]
menu_list = ["📘 Каталог","🛍️ Кошик","📜 Мої замовлення","❓ FAQ","📱 Контакти"]
local_or_delivery_list = ["🚶 Самовивіз", "🚚 Доставка"]
post_type_list= ["Почтомат","Відділення"]
contact_info = "Ви можете забрати своє замовлення за адресою: Вул. 12 Квітня, будинок 3"

engine = create_engine(f"sqlite+pysqlite:///{SRC_PATH}database.db", echo=True)
kratom_engine = create_engine(f"sqlite+pysqlite:///{SRC_PATH}kratom.db", echo=True)

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

LOCALORDELIVERY,ORDER_CORRECT,TEA,HELP,MYORDER,CHECK,TYPE,ORDER,VARIETY, GRAMMS, COUNT,PACKAGE, ASSORTMENT,PERSONAL_INFO,PERSONAL_SURNAME,PERSONAL_PHONE,PERSONAL_CITY,PERSONAL_POST_TYPE,PERSONAL_POST_TYPE_CHOOSE,PERSONAL_INFO_CORRECT,PERSONAL_POST_NUMBER,ASK_UPDATE_PERSONAL,ONE_MORE = range(23)

CATALOG_TYPE, CHOOSE_KRATOM, CHOOSE_GRADE, FOUR = range(4)
GRADE_COUNT = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GRADE_COUNT
    await context.bot.send_message(update.effective_chat.id, 'Вас вітає Kratom Ukraine телеграм бот.👋\nТут ви можете оформити онлайн замовлення або дізнатися детальніше про наш чай 🌱',reply_markup=start_reply_markup)
    context.user_data["ordersid"] = 0

    with Session(kratom_engine) as session:
        GRADE_COUNT = session.query(func.max(Grade.id)).first()[0]
    with Session(engine) as session:
        uid = update.message.from_user.id
        if session.query(User.id).where(User.userid.in_([str(uid)])).first()[0] == None:
            session.add(User(userid=str(uid)))
            session.commit()
    return CHECK

async def myorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session(engine) as session:
        orders = session.query(Orders).where(Orders.user_id.in_([session.query(User.id).where(User.userid == str(update.message.from_user.id)).first()[0]])).join(OrderElements,OrderElements.id == Orders.id,isouter=True)
    await update.message.reply_text(
        f"Це список ваших замовлень:\n",
        reply_markup=start_reply_markup)
    
    tmpstr = ""
    for t in orders:
        tmpstr += f"{t.__repr__()}\n\n"
        for oe in t.orderelements:
            tmpstr += f"{oe.__repr__()}\n\n"
        await update.message.reply_text(tmpstr,parse_mode="Markdown")
        tmpstr = ""

    return CHECK

async def assortment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ви маєте можливість ознайомитися з асортиментом нашого чаю 🌱",
        reply_markup=start_reply_markup,
    )
    return CHECK

async def check_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    option = update.message.text
    if option == menu_list[0]:
        return await catalog(update,context)
    elif option == menu_list[1]:
        return await choose_type(update,context)
    elif option == menu_list[2]:
        return await assortment(update,context) 
    elif option == menu_list[3]:
        return await get_help(update,context)

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🌿Розсипний", callback_data=f"{str(CATALOG_TYPE)}Розсипний"),
            InlineKeyboardButton("💊Капсули", callback_data=f"{str(CATALOG_TYPE)}Капсули"),
        ],
        [
            InlineKeyboardButton("Концентрат", callback_data=f"{str(CATALOG_TYPE)}Концентрат"),
            InlineKeyboardButton("📦Пробний набір", callback_data=f"{str(CATALOG_TYPE)}Пробний"),

        ],
    ]
    context.user_data["current_grade"] = 1
    context.user_data["current_variety"] = 1
    await context.bot.send_photo(chat_id=update.effective_chat.id,
        photo=open(f"images/diagram2.jpg", 'rb'),
        caption="У нашому каталозі ти можеш знайти кратом на будь-який смак 🌱",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def catalog_type_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    context.user_data["type"] = query.data.split(str(CATALOG_TYPE))[1]
    #await update_message_button(update,context)
    await choose_kratom_grade(update,context)

    await query.answer()

async def choose_kratom_grade(update:Update,context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Обрати ✅", callback_data=f"{str(CHOOSE_GRADE)}Обрати")
        ],
        [
            InlineKeyboardButton("⬅️", callback_data=f"{str(CHOOSE_GRADE)}Left"),
            InlineKeyboardButton(f'{context.user_data["current_grade"]}/{GRADE_COUNT}', callback_data=f"{str(CHOOSE_GRADE)}Count"),
            InlineKeyboardButton("➡️", callback_data=f"{str(CHOOSE_GRADE)}Right"),
        ],
        [
            InlineKeyboardButton("Назад", callback_data=f"{str(CHOOSE_GRADE)}Назад"),
            #InlineKeyboardButton("🛍️Сума", callback_data=f"{str(CHOOSE_KRATOM)}Сума"),
        ],
    ]
    query = update.callback_query
    grade = None
    with Session(kratom_engine) as session:
        grade = session.query(Grade).where(Grade.id == context.user_data["current_grade"]).first()
    print(grade)
    await query.edit_message_media( media=InputMediaPhoto(
        media=open(f"images/{grade.img}", 'rb'),
        caption=f"{grade.description}"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_grade_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    current_grade = context.user_data["current_grade"]

    if query.data == f"{str(CHOOSE_GRADE)}Left":
        current_grade -= 1
        if current_grade == 0:
            current_grade = GRADE_COUNT

    elif query.data == f"{str(CHOOSE_GRADE)}Right":
        current_grade += 1
        if current_grade == GRADE_COUNT+1:
            current_grade = 1

    elif query.data == f"{str(CHOOSE_GRADE)}Обрати":
        with Session(kratom_engine) as session:
            context.user_data["variety_count"] = len(session.query(Kratom.id).where(Kratom.grade_id == context.user_data["current_grade"]).first())
        await update_message_button(update,context)

    elif query.data == f"{str(CHOOSE_GRADE)}Назад":
        await context.bot.deleteMessage(message_id=update.effective_message.id,chat_id=update.effective_chat.id)
        await catalog(update,context)
    
    context.user_data["current_grade"] = current_grade
    
    if query.data != f"{str(CHOOSE_GRADE)}Count" and GRADE_COUNT != 1:
        await update_message_button(update,context)
    await query.answer()

async def update_message_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    grade_id = context.user_data["current_grade"]
    query = update.callback_query
    kratom = None
    with Session(kratom_engine) as session:
        kratom_id = session.query(Kratom.id).where(Kratom.grade_id == context.user_data["current_grade"]).first()[context.user_data["current_variety"]-1]
        kratom = session.query(Kratom).where(Kratom.id == kratom_id).join(Kratom.gradecost).first()
        costelement = session.query(CostElement).where(CostElement.id == kratom.gradecost.costelement_id).first()
    print(kratom)
    keyboard = [
        [
            InlineKeyboardButton(f"{costelement.title} {costelement.cost}₴", callback_data=f"{str(CHOOSE_KRATOM)}{costelement.title}"),
        ],
        [
            InlineKeyboardButton("⬅️", callback_data=f"{str(CHOOSE_KRATOM)}Left"),
            InlineKeyboardButton(f'{context.user_data["current_variety"]}/{context.user_data["variety_count"]}', callback_data=f"{str(CHOOSE_KRATOM)}Count"),
            InlineKeyboardButton("➡️", callback_data=f"{str(CHOOSE_KRATOM)}Right"),
        ],
        [
            InlineKeyboardButton("Назад", callback_data=f"{str(CHOOSE_KRATOM)}Назад"),
            InlineKeyboardButton("🛍️Сума", callback_data=f"{str(CHOOSE_KRATOM)}Сума"),

        ],
    ]
    await query.edit_message_media( media=InputMediaPhoto(
        media=open(f"images/{kratom.img}", 'rb'),
        caption=f"{kratom.description}"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_kratom_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    current_variety = context.user_data["current_variety"]
    variety_count = context.user_data["variety_count"]

    if query.data == f"{str(CHOOSE_KRATOM)}Left":
        current_variety -= 1
        if current_variety == 0:
            current_variety = variety_count

    elif query.data == f"{str(CHOOSE_KRATOM)}Right":
        current_variety += 1
        if current_variety == variety_count+1:
            current_variety = 1

    elif query.data == f"{str(CHOOSE_KRATOM)}Назад":
        #await context.bot.deleteMessage(message_id=update.effective_message.id,chat_id=update.effective_chat.id)
        #await catalog(update,context)
        await choose_kratom_grade(update,context)
    
    context.user_data["current_variety"] = current_variety
    
    if query.data != f"{str(CHOOSE_KRATOM)}Count" and variety_count != 1:
        await update_message_button(update,context)
    await query.answer()

async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Контакт нашого менеджера:\n ☎️*+380991234567* - Іван\n☎️ *+380991234567* - Некто\n📧 *https://t.me/kratom_ukrainee* - KratomUkraine",
        reply_markup=start_reply_markup,
        parse_mode="Markdown"
    )
    return CHECK

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Розсипний","Капсули"],["Концентрат","Пробний набір"]],one_time_keyboard=True,resize_keyboard=True)
    await context.bot.send_message(update.effective_chat.id, '📦 Оберіть зручну форму пакування',reply_markup=reply_markup)
    return TEA

async def choose_tea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    type = update.message.text
    context.user_data["type"] = type
    logger.info("%s TYPE", type)
    options_matrix = [
        ["Maeng da Білий", "Maeng da Зелений"],
        ["Maeng da Червоний", "Тайський зелений"],
        ["Борнео червоний", "Білий Слон"],
        ["Шива", "White Honey"],
        ["Богиня Калі", "Golden Dragon"],
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
    reply_markup = ReplyKeyboardMarkup([["Так","Ні"]],one_time_keyboard=True,resize_keyboard=True)
    if update.message.text == "Так":
        with Session(engine) as session:
            if context.user_data["ordersid"] == 0:
                uid = session.query(User.id).where(User.userid.in_([str(update.message.from_user.id)])).first()[0]
                times = int(time.time())
                tmp = Orders(time = times,user_id=uid)
                session.add(tmp)
                session.commit()
                context.user_data["ordersid"] = session.query(Orders.id).where(Orders.time.in_([times])).first()[0]

            tmpoe = OrderElements(tea=context.user_data["variety"],weight=context.user_data["gramms"],amount=context.user_data["package"],type=context.user_data["type"],order_id=context.user_data["ordersid"])
            
            session.add_all([tmpoe])
            session.commit()

        await update.message.reply_text("Бажаєте додати ще один сорт ?", reply_markup=reply_markup)
        return ONE_MORE
    else:
        return await choose_type(update,context) 
    
async def one_more_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Так":
        return await choose_type(update,context)
    else:
        await update.message.reply_text("📦 Оберіть зручний для вас вид доставки\n\n🚶 Самовивіз\nВи маєте можливість особисто забрати замовлення у зручний для Вас час у проміжок часу (11:00 - 18:00).\n\n🚚 Доставка поштою\nВаше замовлення буде надіслано протягом робочого дня за тарифами Нової Пошти.",
            reply_markup=ReplyKeyboardMarkup([local_or_delivery_list],one_time_keyboard=True,input_field_placeholder="",resize_keyboard=True)
        )
        return LOCALORDELIVERY
    
async def local_or_delivery(update: Update,context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Так","Ні"]],one_time_keyboard=True,resize_keyboard=True)
    lod = update.message.text
    if(lod == local_or_delivery_list[0]):
        return await local(update,context)
    else:
        with Session(engine) as session:
            user = session.query(User).where(User.userid.in_([str(update.message.from_user.id)])).first()
        if user.name != None:
            await update.message.reply_text(f"{user}")
            await update.message.reply_text("Інформація актуальна ?", reply_markup=reply_markup)
            return ASK_UPDATE_PERSONAL
        else:
            return await personal_info_name(update,context)

async def ask_update_personal(update: Update,context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Так":
        await update.message.reply_text("Щиро дякуємо за замовлення !",
            reply_markup=start_reply_markup)
        return CHECK
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
    user = User(name=context.user_data["name"],surname=context.user_data["surname"],phone=context.user_data["phone"],city=context.user_data["city"],post_type=context.user_data["post_type"],post_number=post_number)
    await update.message.reply_text(
        f"{user}\nВсе вказано вірно ?",
        reply_markup=reply_markup,
    )
    return PERSONAL_INFO_CORRECT

async def is_personal_info_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Так":
        with Session(engine) as session:
            user = session.query(User).where(User.userid.in_([str(update.message.from_user.id)])).first()
            user.name = context.user_data["name"]
            user.surname = context.user_data["surname"]
            user.phone = context.user_data["phone"]
            user.city = context.user_data["city"]
            user.post_type = context.user_data["post_type"]
            user.post_number = context.user_data["post_number"]
            session.commit()
        context.user_data["ordersid"] = 0
        await update.message.reply_text("Щиро дякуємо за замовлення !",
            reply_markup=start_reply_markup)
        return CHECK
    else:
        return await personal_info_name(update,context) 

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ordersid"] = 0
    await context.bot.send_message(update.effective_chat.id, 'Замовлення призупинено')

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(ConversationHandler(
        entry_points=[CommandHandler(["start","hello"], start),[MessageHandler(filters.Regex(gen_regex(menu_list)),check_menu)]],
        states={
            CHECK: [
                MessageHandler(filters.Regex(gen_regex(menu_list)),check_menu),
                CallbackQueryHandler(catalog_type_check, pattern="^"+str(CATALOG_TYPE)+".*$"),
                CallbackQueryHandler(choose_kratom_check, pattern="^"+str(CHOOSE_KRATOM)+".*$"),
                CallbackQueryHandler(choose_grade_check, pattern="^"+str(CHOOSE_GRADE)+".*$")
                ],
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
            ASK_UPDATE_PERSONAL:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),ask_update_personal)],
            ONE_MORE:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),one_more_ask)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
app.run_polling()