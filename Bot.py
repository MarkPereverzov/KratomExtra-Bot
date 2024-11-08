from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, ApplicationBuilder,ConversationHandler, MessageHandler,filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
import logging
import time
from typing import List
from bottoken import TOKEN
from classes import User,OrderElements,Orders, Kratom, Grade,TypeCost,CostElement,CostElementModel, CostOrderElement
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
start_reply_markup = ReplyKeyboardMarkup([["📘 Каталог","🛍️ Кошик"],["📜 Мої замовлення","📱 Контакти" ],["❓ FAQ"]],one_time_keyboard=True,input_field_placeholder="Сорт",resize_keyboard=True)
gramms_list = ["10 г", "25 г", "50 г", "100 г", "1 кг"]
choose_type_list = ["🌿Розсипний","💊Капсули","🍬Цукерки","📦Пробний набір"]
menu_list = ["📘 Каталог","🛍️ Кошик","📜 Мої замовлення","📱 Контакти","❓ FAQ"]
local_or_delivery_list = ["🚶 Самовивіз", "🚚 Доставка"]
post_type_list= ["Почтомат","Відділення"]
contact_info = "Ви можете забрати своє замовлення за адресою: Вул. 12 Квітня, будинок 3"

#engine = create_engine(f"sqlite+pysqlite:///{SRC_PATH}database.db", echo=True)
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

LOCALORDELIVERY,ORDER_CORRECT,TEA,HELP,MYORDER,CHECK,TYPE,ORDER,VARIETY, GRAMMS, COUNT,PACKAGE, ASSORTMENT,PERSONAL_INFO,PERSONAL_NAME,PERSONAL_PHONE,PERSONAL_ADDRESS,PERSONAL_INFO_CORRECT,ASK_UPDATE_PERSONAL,ONE_MORE = range(20)

CATALOG_TYPE, CHOOSE_KRATOM, CHOOSE_GRADE, CHOOSE_COST, CHANGE_COUNT, SHOPING_CARD, CHOOSE_EDIT_KRATOM = range(7)
GRADE_COUNT = 0

async def reset(update,context):
    context.user_data["ordersid"] = 0
    context.user_data["current_costelement"] = None
    context.user_data["current_orderelement"] = None
    context.user_data["order"] = []
    context.user_data["current_sum"] = "Кошик"
    context.user_data["flag_edit"] = False
    context.user_data["message_shopingcard"] = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GRADE_COUNT
    await context.bot.send_message(update.effective_chat.id, 'Вітаємо вас в *KRATOM EXTRA* телеграм бот👋\nТут ви можете оформити онлайн замовлення або дізнатися детальніше про наш чай🌱',parse_mode= 'Markdown', reply_markup=start_reply_markup)
    await reset(update,context)

    with Session(kratom_engine) as session:
        GRADE_COUNT = session.query(func.max(Grade.id)).first()[0]
    with Session(kratom_engine) as session:
        uid = update.message.from_user.id
        if session.query(User.id).where(User.userid.in_([str(uid)])).first() == None:
            session.add(User(userid=str(uid)))
            session.commit()
    return CHECK

async def myorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with Session(kratom_engine) as session:
        orders = session.query(Orders).where(Orders.user_id.in_([session.query(User.id).where(User.userid == str(update.message.from_user.id)).first()[0]]))
        orders.join(OrderElements,OrderElements.id == Orders.id,isouter=True)
        orders.join(CostOrderElement,CostOrderElement.orderelement_id == OrderElements.id,isouter=True)
        orders.join(Kratom,Kratom.id == OrderElements.kratom_id,isouter=True)
        orders.join(CostElement,CostOrderElement.costelement_id == CostElement.id,isouter=True)
        
    exstflag = False
    for t in orders:
        exstflag = True

    await update.message.reply_text(
        f"{'Це список ваших замовлень:' if exstflag else 'У вас ще не було замовлень'}\n",
        reply_markup=start_reply_markup)

    tmpstr = ""
    for t in orders:
        if len(t.orderelements) > 0:
            tmpstr += f"{t.__repr__()}\n"
            for oe in t.orderelements:
                tmpstr += f"{oe.__repr__()}\n\n"
            await update.message.reply_text(tmpstr,parse_mode="Markdown")
            tmpstr = ""

    return CHECK

async def assortment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ви маєте можливість ознайомитися з асортиментом нашого чаю 🌱",
        reply_markup=start_reply_markup,
        parse_mode= 'Markdown',
    )
    return CHECK

async def check_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    option = update.message.text
    if option == menu_list[0]:
        return await catalog(update,context)
    elif option == menu_list[1]:
        return await shopingcard(update,context)
        #return await choose_type(update,context)
    elif option == menu_list[2]:
        #return await assortment(update,context) 
        return await myorder(update,context)
    elif option == menu_list[3]:
        return await get_help(update,context)
    elif option == menu_list[4]:
        return await frequently_asked_questions(update,context)

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["flag_edit"] = False
    context.user_data["message_shopingcard"] = None


    keyboard = [
        [
            InlineKeyboardButton("🌿Розсипний", callback_data=f"{str(CATALOG_TYPE)}Розсипний"),
            InlineKeyboardButton("💊Капсули", callback_data=f"{str(CATALOG_TYPE)}Капсули"),
        ],
        [
            InlineKeyboardButton("🍬Цукерки", callback_data=f"{str(CATALOG_TYPE)}Концентрат"),
            InlineKeyboardButton("📦Пробний набір", callback_data=f"{str(CATALOG_TYPE)}Пробний"),

        ],
    ]
    
    context.user_data["current_grade"] = 1
    context.user_data["current_variety"] = 1

    await context.bot.send_photo(chat_id=update.effective_chat.id,
        photo=open(f"images/logo.png", 'rb'),
        caption="Ознайомтеся з нашим асортиментом: розсипний, капсули, конфети або випробуйте наш пробний набір. \n\nОбирайте те, що вам до вподоби, і насолоджуйтеся унікальним досвідом від *KRATOM EXTRA*.",
        parse_mode= 'Markdown',
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
    await query.edit_message_media( 
        media=InputMediaPhoto(
        media=open(f"images/{grade.img}", 'rb'),
        caption=f"{grade.description}",
        parse_mode="Markdown",
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_grade_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    current_grade = context.user_data["current_grade"]

    if query.data == f"{str(CHOOSE_GRADE)}Left":
        current_grade -= 1
        if current_grade == 0:
            current_grade = GRADE_COUNT
        context.user_data["current_grade"] = current_grade
        await choose_kratom_grade(update,context)

    elif query.data == f"{str(CHOOSE_GRADE)}Right":
        current_grade += 1
        if current_grade == GRADE_COUNT+1:
            current_grade = 1
        context.user_data["current_grade"] = current_grade
        await choose_kratom_grade(update,context)

    elif query.data == f"{str(CHOOSE_GRADE)}Назад":
        await context.bot.deleteMessage(message_id=update.effective_message.id,chat_id=update.effective_chat.id)
        await catalog(update,context)
        
    elif query.data == f"{str(CHOOSE_GRADE)}Обрати":
        with Session(kratom_engine) as session:
            context.user_data["current_variety"] = 1
            context.user_data["variety_count"] = len(session.query(Kratom.id).where(Kratom.grade_id == context.user_data["current_grade"]).all())
        await update_from_database(update,context)
        await update_message_button(update,context)

    await query.answer()

async def update_from_database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    grade_id = context.user_data["current_grade"]

    with Session(kratom_engine) as session:
        kratom_id = session.query(Kratom.id).where(Kratom.grade_id == grade_id).all()[context.user_data["current_variety"]-1][0]
        context.user_data["current_kratom_id"] = kratom_id
        kratom = session.query(Kratom).where(Kratom.id == kratom_id).first()
        context.user_data["current_kratom_variety"] = kratom.variety
        typecosts = session.query(TypeCost.id).where(and_(TypeCost.grade_id == kratom.grade_id,TypeCost.type == context.user_data["type"])).all()

        tmptypecostid = []
        for typecost in typecosts:
            tmptypecostid.append(typecost[0])

        costelements = session.query(CostElement).where(CostElement.id.in_(tmptypecostid)).all()

    context.user_data["kratom"] = kratom
    context.user_data["costelements"] = costelements

async def update_message_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    kratom = context.user_data["kratom"]
    kel = []

    for costelement in context.user_data["costelements"]:
        flag = False
        if context.user_data["current_orderelement"] != None:
            if context.user_data["current_costelement_id"] == int(costelement.id) and context.user_data["current_orderelement"].kratom_id == kratom.id:
                flag = True
                for x in context.user_data["current_orderelement"].costorderelement:
                    if context.user_data["current_costelement_id"] == x.costelement_id:
                        context.user_data['current_costorderelement'] = x
        if flag:
            kel.append([
                InlineKeyboardButton("-1",callback_data=f"CHANGE_COUNT-1CHANGE_COUNT{costelement.id}"),
                InlineKeyboardButton(f"✏️ {context.user_data['current_costorderelement'].count} Редагувати",callback_data=f"CHANGE_COUNTРедагуватиCHANGE_COUNT{costelement.id}"),
                InlineKeyboardButton("+1",callback_data=f"CHANGE_COUNT+1CHANGE_COUNT{costelement.id}"),
                ])
        else:
            kel.append([InlineKeyboardButton(f"{costelement.count}\t{costelement.title}\t{costelement.cost}₴", callback_data=f"CHOOSE_COST{costelement.id}")])

    kel.append([
            InlineKeyboardButton("⬅️", callback_data=f"{str(CHOOSE_KRATOM)}Left"),
            InlineKeyboardButton(f'{context.user_data["current_variety"]}/{context.user_data["variety_count"]}', callback_data=f"{str(CHOOSE_KRATOM)}Count"),
            InlineKeyboardButton("➡️", callback_data=f"{str(CHOOSE_KRATOM)}Right"),
            ])
    kel.append([
            InlineKeyboardButton("Назад", callback_data=f"{str(CHOOSE_KRATOM)}Назад"),
            InlineKeyboardButton(f"🛍️{context.user_data['current_sum']}", callback_data=f"{str(CHOOSE_KRATOM)}Сума"),
            ])
    await query.edit_message_media( media=InputMediaPhoto(
        media=open(f"images/{kratom.img}", 'rb'),
        caption=f"{kratom.description}",
        parse_mode="Markdown",
        ),
        reply_markup=InlineKeyboardMarkup(kel)
    )

async def choose_kratom_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    current_variety = context.user_data["current_variety"]
    variety_count = context.user_data["variety_count"]

    if query.data == f"{str(CHOOSE_KRATOM)}Left":
        current_variety -= 1
        if current_variety == 0:
            current_variety = variety_count
        context.user_data["current_variety"] = current_variety
        await update_from_database(update,context)
        await update_message_button(update,context)

    elif query.data == f"{str(CHOOSE_KRATOM)}Right":
        current_variety += 1
        if current_variety == variety_count+1:
            current_variety = 1
        context.user_data["current_variety"] = current_variety
        await update_from_database(update,context)
        await update_message_button(update,context)

    elif query.data == f"{str(CHOOSE_KRATOM)}Назад":
        await choose_kratom_grade(update,context)
    
    elif query.data == f"{str(CHOOSE_KRATOM)}Сума":
        await context.bot.deleteMessage(message_id=update.effective_message.id,chat_id=update.effective_chat.id)
        await shopingcard(update,context)

    await query.answer()

async def choose_cost_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    current_variety = context.user_data["current_variety"]
    current_kratom_id = context.user_data["current_kratom_id"]
    context.user_data["current_orderelement"] = next((x for x in context.user_data["order"] if x.kratom_id == current_kratom_id ), None)
    
    if context.user_data["current_orderelement"] != None:
        context.user_data["current_costelement_id"] = int(query.data.split("CHOOSE_COST")[1])
        costorderelement_current = None
        for y in context.user_data["current_orderelement"].costorderelement:
            if y.costelement_id == int(query.data.split("CHOOSE_COST")[1]):
                costorderelement_current = y
                break
        if costorderelement_current != None:
            costorderelement_current.count += 1
        else:
            with Session(kratom_engine) as session:
                tmp_costelement = session.query(CostElement).where(CostElement.id == int(query.data.split("CHOOSE_COST")[1])).first()
            costorderelement_current = CostOrderElement(costelement_id = tmp_costelement.id, costelement = tmp_costelement,orderelement_id = context.user_data["current_orderelement"].id,orderelement = context.user_data["current_orderelement"],count=1)
    else:
        oes = OrderElements(costorderelement=[],kratom_id=current_kratom_id,kratom=context.user_data["kratom"],type=context.user_data["type"])
        with Session(kratom_engine) as session:
            costelement = session.query(CostElement).where(CostElement.id == int(query.data.split("CHOOSE_COST")[1])).first()
            oes.costorderelement = [CostOrderElement(costelement=costelement,costelement_id=costelement.id,orderelement=oes,orderelement_id=oes.id,count=1)]

        context.user_data["current_costelement_id"] = costelement.id
        context.user_data["current_orderelement"] = oes
        context.user_data["order"].append(context.user_data["current_orderelement"])

    #for order in context.user_data["order"].orderelements:
        #UPDATE BUTTON

    #calculate order cost
    await generateorderlist(update,context)

    await query.answer()
    await update_message_button(update,context)

async def change_count_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    value = query.data.split("CHANGE_COUNT")[1]

    costelement_id = int(query.data.split("CHANGE_COUNT")[2])

    if value == "+1":
        if context.user_data["current_orderelement"] != None:
            for x in context.user_data["current_orderelement"].costorderelement:
                if x.costelement.id == costelement_id:
                    x.count += 1

    elif value == "-1":
        if context.user_data["current_orderelement"] != None:
            for x in context.user_data["current_orderelement"].costorderelement:
                if x.costelement.id == costelement_id:
                    x.count -= 1
                if x.count < 0: x.count = 0

    #calculate order cost
    await generateorderlist(update,context)

    await query.answer()
    await update_message_button(update,context)

async def generateorderlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    grouped_order = context.user_data["order"]
    known_kratom_id = []

    # for h in context.user_data["order"]:
    #     kid_flag = True
    #     for kid in known_kratom_id:
    #         if kid == h.kratom_id:
    #             kid_flag = False
    #     if kid_flag:
    #         known_kratom_id.append(h.kratom_id)
    
    # for i in known_kratom_id:
    #     for j in grouped_order:
    #         next((x for x in j if j.kratom_id), None)
    #     grouped_orderelement = [x for x in context.user_data["order"] if x.kratom_id == i]
    #     add_flag = True
    #     if len(grouped_orderelement) != 0:
    #         grouped_order.append(grouped_orderelement)

    #//context.user_data["grouped_order"] = grouped_order

    outstr = "*Кошик*\n"
    summ = 0
    #for orderelement in context.user_data["order"]:
    #print(grouped_order)

    for x in context.user_data["order"][0].costorderelement:
        print(f"{x.costelement.cost}\t{x.costelement.count}\t{x.count}")

    for order in grouped_order:
        name_variety_str = f"*{order.type} {order.kratom.variety}*\n"
        outstr += f"\n{'-'*35}\n"
        outstr += name_variety_str
        for orderelement in order.costorderelement:
            tmpsum = int(orderelement.count)*int(orderelement.costelement.cost)
            summ += tmpsum
            outstr += f"{orderelement.costelement.count} {orderelement.costelement.title}: {orderelement.count} x {orderelement.costelement.cost}₴ = {tmpsum}₴\n"

        outstr += f"{'-'*35}\n"

    context.user_data["current_sum"] = f"{summ}₴"
    outstr += f"\n*Загалом*: {summ}₴"

    return outstr

async def shopingcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_orderelement'] = None
    context.user_data["current_edit_orderelement"] = 1
    context.user_data["current_costelement_id"] = -1

    if len(context.user_data["order"]) == 0:
        await context.bot.send_message(update.effective_chat.id,
            "Зробіть замовлення, щоб побачити його тут!",
            reply_markup=start_reply_markup,
            parse_mode="Markdown"
        )
    else:
        keyboard = [
            [
                InlineKeyboardButton("✏️Редагувати",callback_data=f"{str(SHOPING_CARD)}Редагувати"),
                InlineKeyboardButton("❌Видалити",callback_data=f"{str(SHOPING_CARD)}Видалити"),
            ],
            [InlineKeyboardButton("✅Оформити замовлення",callback_data=f"{str(SHOPING_CARD)}Оформити")]
        ]
        if context.user_data["message_shopingcard"] == None:
            context.user_data["message_shopingcard"] = await context.bot.send_message(update.effective_chat.id,f"{await generateorderlist(update,context)}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )
        else:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id,message_id=context.user_data["message_shopingcard"].message_id,text=f"{await generateorderlist(update,context)}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )
        return CHECK

async def shopingcard_check(update: Update,context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer() 

    if query.data == f"{str(SHOPING_CARD)}Видалити":
        context.user_data["order"] = []
        await context.bot.deleteMessage(message_id=update.effective_message.id,chat_id=update.effective_chat.id)
        await shopingcard(update,context)

    elif query.data == f"{str(SHOPING_CARD)}Редагувати":
        await shopingcard_edit(update,context)

    elif query.data == f"{str(SHOPING_CARD)}Оформити":
        return await one_more_ask(update,context)

async def update_edit_button(update: Update,context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    order = context.user_data["order"]
    orderelement = order[context.user_data['current_edit_orderelement']-1]
    context.user_data["current_orderelement"] = orderelement
    kratom = orderelement.kratom
    kel = []

    caption_gen = f"*{orderelement.type} {kratom.variety}*\n"

    for x in orderelement.costorderelement:
        if x.costelement.id == context.user_data["current_costelement_id"]:
            kel.append([
                InlineKeyboardButton("-1",callback_data=f"CHANGE_EDIT_COUNT-1CHANGE_EDIT_COUNT{x.costelement.id}"),
                InlineKeyboardButton(f"✏️ {x.count}",callback_data=f"CHANGE_EDIT_COUNTРедагувати"),
                InlineKeyboardButton("+1",callback_data=f"CHANGE_EDIT_COUNT+1CHANGE_EDIT_COUNT{x.costelement.id}"),
                ])
        else:
            kel.append([InlineKeyboardButton(f"✏️ {x.count} {orderelement.type} | {x.costelement.cost}₴\t{x.costelement.count}\t{x.costelement.title}", callback_data=f"CHOOSE_EDIT_COST{x.costelement.id}")])

        caption_gen += f"\n{x.costelement.count} {x.costelement.title}: {x.count} {orderelement.type} x {x.costelement.cost}₴ = {x.costelement.cost*x.count}₴"

    kel.append([
            InlineKeyboardButton("⬅️", callback_data=f"{str(CHOOSE_EDIT_KRATOM)}Left"),
            InlineKeyboardButton(f'{context.user_data["current_edit_orderelement"]}/{len(order)}', callback_data=f"{str(CHOOSE_EDIT_KRATOM)}Count"),
            InlineKeyboardButton("➡️", callback_data=f"{str(CHOOSE_EDIT_KRATOM)}Right"),
        ])
    kel.append([
            InlineKeyboardButton(f"✅Завершити редагування", callback_data=f"{str(CHOOSE_EDIT_KRATOM)}Сума"),
        ])
        
    if context.user_data["flag_edit"]:
        await query.edit_message_media(media=InputMediaPhoto(
            media=open(f"images/{kratom.img}", 'rb'),
            caption=f"{caption_gen}",
            parse_mode= 'Markdown'),
            reply_markup=InlineKeyboardMarkup(kel)
        )
    else:
        context.user_data["flag_edit"] = True
        await context.bot.send_photo(chat_id=update.effective_chat.id,
            photo=open(f"images/{kratom.img}", 'rb'),
            caption=f"{caption_gen}",
            parse_mode= 'Markdown',
            reply_markup=InlineKeyboardMarkup(kel)
        )

async def choose_cost_edit_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["current_costelement_id"] = int(update.callback_query.data.split("CHOOSE_EDIT_COST")[1])

    await update.callback_query.answer()
    await update_edit_button(update,context)

async def change_count_edit_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    value = query.data.split("CHANGE_EDIT_COUNT")[1]

    costelement_id = int(query.data.split("CHANGE_EDIT_COUNT")[2])

    if value == "+1":
        if context.user_data["current_orderelement"] != None:
            for x in context.user_data["current_orderelement"].costorderelement:
                if x.costelement.id == costelement_id:
                    x.count += 1

    elif value == "-1":
        if context.user_data["current_orderelement"] != None:
            for x in context.user_data["current_orderelement"].costorderelement:
                if x.costelement.id == costelement_id:
                    x.count -= 1
                if x.count < 0: x.count = 0

    await query.answer()
    await update_edit_button(update,context)

async def check_update_edit(update:Update,context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    current_edit_orderelement = context.user_data['current_edit_orderelement']

    if query.data == f"{str(CHOOSE_EDIT_KRATOM)}Left":
        current_edit_orderelement -= 1
        if current_edit_orderelement == 0:
            current_edit_orderelement = len(context.user_data["order"])
        context.user_data['current_edit_orderelement'] = current_edit_orderelement
        context.user_data["current_costelement_id"] = -1
        await shopingcard_edit(update,context)

    elif query.data == f"{str(CHOOSE_EDIT_KRATOM)}Right":
        current_edit_orderelement += 1
        if current_edit_orderelement == len(context.user_data["order"])+1:
            current_edit_orderelement = 1
        context.user_data['current_edit_orderelement'] = current_edit_orderelement
        context.user_data["current_costelement_id"] = -1
        await shopingcard_edit(update,context)
    
    elif query.data == f"{str(CHOOSE_EDIT_KRATOM)}Сума":
        await context.bot.deleteMessage(message_id=update.effective_message.id,chat_id=update.effective_chat.id)
        await shopingcard(update,context)
        
    # elif query.data == f"{str(CHOOSE_GRADE)}Обрати":
    #     with Session(kratom_engine) as session:
    #         context.user_data["current_variety"] = 1
    #         context.user_data["variety_count"] = len(session.query(Kratom.id).where(Kratom.grade_id == context.user_data["current_grade"]).all())
    #     await update_from_database(update,context)
    #     await update_message_button(update,context)

    await query.answer()

async def shopingcard_edit(update: Update,context: ContextTypes.DEFAULT_TYPE):
    # keyboard = [
    #         [
    #             InlineKeyboardButton("✏️Редагувати",callback_data=f"{str(SHOPING_CARD)}Редагувати"),
    #             InlineKeyboardButton("❌Видалити",callback_data=f"{str(SHOPING_CARD)}Видалити"),
    #         ],
    #         [InlineKeyboardButton("✅Оформити замовлення",callback_data=f"{str(SHOPING_CARD)}Оформити")]
    # ]

    # order = context.user_data["order"]
    # orderelement = order[context.user_data['current_edit_orderelement']]
    # kratom = orderelement.kratom

    # await context.bot.send_photo(chat_id=update.effective_chat.id,
    #     photo=open(f"images/{kratom.img}", 'rb'),
    #     caption="",
    #     parse_mode= 'Markdown',
    #     reply_markup=InlineKeyboardMarkup(keyboard)
    # )
    await update_edit_button(update,context)

    return CHECK

async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Якщо у вас виникли питання або труднощі, звертатеся до нашого менеджера - 👤 @account\n\nТакож ви можете знайти корисну інформацію у нашому каналі в Telegram:",
        reply_markup=start_reply_markup,
        parse_mode="Markdown"
    )
    return CHECK

async def frequently_asked_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Як здійснити своє перше замовлення від нас?*\nУ вас є можливість вибрати будь-який продукт з нашого каталогу, розташованого в інтернет-магазині. Просто виберіть сорт, який вам подобається, та вказіть бажану вагу. Оплатити своє замовлення можна, натиснув на кнопку 🛍 кошик у вікні замовлення та слідуючи інструкціям.\n\n*Які сорти є в наявності?*\nМи завжди ретельно стежимо за тим, щоб наші сорти залишалися в наявності і демонструємо вам наш асортимент.\n\n*STANDARD*\n🌿 Maeng Da Green\n🌿 White Elephant\n🌿 Red Borneo\n\n*PREMIUM*\n🌿 Red Borneo\n🌿 Yellow Dragon\n🌿 Super Green\n\n*EXTRA PREMIUM*\n🌿 Kali\n🌿 Kama\n\n*Які варіанти доставки ми маємо?*\n🚚 Доставка на відділення Нової Пошти\n🚕 Відправлення за допомогою таксі\n🚶🏻‍♂️ Самовивіз\n\n*У який час можна робити замовлення та коли його відправлять?*\nВи можете зробити замовлення в будь який зручний для вас час. Якщо замовлення оформлено до 12:00 або 16:30, ми відправимо його о першій або другій половині того ж дня.",
        reply_markup=start_reply_markup,
        parse_mode="Markdown"
    )
    return CHECK
    
async def one_more_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,text="📦 *Оберіть зручний для вас вид доставки:*\n\n🚶 *Самовивіз*\nВи маєте можливість особисто забрати замовлення у зручний для Вас час у проміжок часу (11:00 - 18:00).\n\n🚚 *Доставка поштою*\nВаше замовлення буде надіслано протягом робочого дня за тарифами Нової Пошти.",
        reply_markup=ReplyKeyboardMarkup([local_or_delivery_list],one_time_keyboard=True,input_field_placeholder="",resize_keyboard=True),
        parse_mode="Markdown"
    )
    await context.bot.deleteMessage(message_id=update.effective_message.id,chat_id=update.effective_chat.id)
    return LOCALORDELIVERY
    
async def local_or_delivery(update: Update,context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Так","Ні"]],one_time_keyboard=True,resize_keyboard=True)
    lod = update.message.text
    if(lod == local_or_delivery_list[0]):
        await send_order_to_chat(update,context,True)
        await save_order_to_db(context,1)
        await reset(update,context)
        return await local(update,context)
    else:
        with Session(kratom_engine) as session:
            user = session.query(User).where(User.userid.in_([str(update.message.from_user.id)])).first()
        if user.name != None:
            await update.message.reply_text(f"{user}")
            await update.message.reply_text("Інформація актуальна ?", reply_markup=reply_markup)
            return ASK_UPDATE_PERSONAL
        else:
            return await personal_info(update,context)

async def save_order_to_db(context,user_id):
    if len(context.user_data["order"]) > 0:
        with Session(kratom_engine) as session:
            order = Orders(user_id=user_id)
            session.add(order)
            session.commit()
            session.refresh(order)
            for x in context.user_data["order"]:
                x.order_id = order.id
                session.add(x)
                session.commit()
                for y in x.costorderelement:
                    session.add(y)
                    session.commit()

async def ask_update_personal(update: Update,context: ContextTypes.DEFAULT_TYPE):
    with Session(kratom_engine) as session:
        user = session.query(User).where(User.userid.in_([str(update.message.from_user.id)])).first()
        context.user_data["name"] = user.name
        context.user_data["address"] = user.adress
        context.user_data["phone"] = user.phone
    if update.message.text == "Так":
        await update.message.reply_text("Щиро дякуємо за замовлення !",
            reply_markup=start_reply_markup)
        await send_order_to_chat(update,context)
        await save_order_to_db(context,user.id)
        await reset(update,context)
        return CHECK
    else:
        return await personal_info(update,context) 

async def local(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        contact_info+"\nЩиро дякуємо за замовлення!",
        reply_markup=start_reply_markup
    )
    return CHECK

async def personal_info(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("*Введіть ПІБ* \nприклад (Васильчук Василь Васильович)", reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    return PERSONAL_NAME

async def personal_info_name(update: Update,context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data["name"] = name
    await update.message.reply_text("*Введіть адресу* \nприклад (м. Запоріжжя, відділення 11)", parse_mode="Markdown")
    return PERSONAL_ADDRESS

async def personal_info_address(update: Update,context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text
    context.user_data["address"] = address
    await update.message.reply_text("*Введіть номер телефону* \nприклад (+38 073 00 000 00)", parse_mode="Markdown")
    return PERSONAL_PHONE

async def personal_info_phone(update: Update,context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["Так","Ні"]],one_time_keyboard=True,resize_keyboard=True)
    phone = update.message.text
    context.user_data["phone"] = phone
    userid = update.message.from_user.id
    user = User(name=context.user_data["name"],phone=context.user_data["phone"],adress=context.user_data["address"])
    await update.message.reply_text(
        f"{user}\nВсе вказано вірно?",
        reply_markup=reply_markup,
    )
    return PERSONAL_INFO_CORRECT

async def is_personal_info_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Так":
        with Session(kratom_engine) as session:
            user = session.query(User).where(User.userid.in_([str(update.message.from_user.id)])).first()
            user.name = context.user_data["name"]
            user.phone = context.user_data["phone"]
            user.adress = context.user_data["address"]
            session.commit()
        context.user_data["ordersid"] = 0
        await update.message.reply_text("Щиро дякуємо за замовлення !",
            reply_markup=start_reply_markup)
        await send_order_to_chat(update,context)
        await save_order_to_db(context,user.id)
        await reset(update,context)
        return CHECK
    else:
        return await personal_info_name(update,context) 

async def send_order_to_chat(update: Update,context: ContextTypes.DEFAULT_TYPE, sam=False):
    if not sam:
        user = User(name=context.user_data["name"],phone=context.user_data["phone"],adress=context.user_data["address"])
        linked_user = f'[username](tg://user?id={update.effective_user.id})'
        outstr = "*Замовлення: *\n"
    for x in context.user_data["order"]:
        outstr += f"{x}"

    if sam:
        await context.bot.send_message(chat_id='-1002132689235',text=f"{outstr}\n{'Самовивіз'}\n{linked_user}",parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id='-1002132689235',text=f"{outstr}\n{user}\n{linked_user}",parse_mode='Markdown')

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
                CallbackQueryHandler(choose_grade_check, pattern="^"+str(CHOOSE_GRADE)+".*$"),
                CallbackQueryHandler(choose_cost_check, pattern="^CHOOSE_COST.*$"),
                CallbackQueryHandler(change_count_check, pattern="^CHANGE_COUNT.*$"),
                CallbackQueryHandler(shopingcard_check, pattern="^"+str(SHOPING_CARD)+".*$"),
                CallbackQueryHandler(check_update_edit, pattern="^"+str(CHOOSE_EDIT_KRATOM)+".*$"),
                CallbackQueryHandler(choose_cost_edit_check, pattern="^CHOOSE_EDIT_COST.*$"),
                CallbackQueryHandler(change_count_edit_check, pattern="^CHANGE_EDIT_COUNT.*$"),
                ],
            # TEA: [MessageHandler(filters.TEXT,choose_tea)],
            # VARIETY: [MessageHandler(filters.Regex(gen_regex(variety_dict["UA"])), variety_select)],
            # GRAMMS: [MessageHandler(filters.Regex(gen_regex(gramms_list)), gramms_select)],
            # PACKAGE: [MessageHandler(filters.Regex("^[0-9]+$"),package_select)],
            # ORDER_CORRECT:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),is_oreder_correct)],
            LOCALORDELIVERY:[MessageHandler(filters.Regex(gen_regex(local_or_delivery_list)),local_or_delivery)],
            PERSONAL_INFO:[MessageHandler(filters.TEXT,personal_info)],
            PERSONAL_NAME:[MessageHandler(filters.TEXT,personal_info_name)],
            PERSONAL_PHONE:[
                #MessageHandler(filters.Regex("[+0-9]{9,13}"),personal_info_phone),
                MessageHandler(filters.TEXT,personal_info_phone),
                ],            
            PERSONAL_ADDRESS:[MessageHandler(filters.TEXT,personal_info_address)],
            PERSONAL_INFO_CORRECT:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),is_personal_info_correct)],
            ASK_UPDATE_PERSONAL:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),ask_update_personal)],
            ONE_MORE:[MessageHandler(filters.Regex(gen_regex(["Так","Ні"])),one_more_ask)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
app.run_polling()