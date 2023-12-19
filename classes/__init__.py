from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
import time
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    userid: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30),nullable=True)
    surname: Mapped[str] = mapped_column(String(30),nullable=True)
    phone: Mapped[str] = mapped_column(String(30),nullable=True)
    city: Mapped[str] = mapped_column(String(30),nullable=True)
    post_type: Mapped[str] = mapped_column(String(30),nullable=True)
    post_number: Mapped[int] = mapped_column(nullable=True)
    orders: Mapped[List["Orders"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"Ім'я: {self.name}\nПрізвище: {self.surname}\n"+f"Телефон: {self.phone}\nМісто: {self.city}\n"+f"Почтомат/відділення: {self.post_type}\n"+f"Номер почтомату/відділення: {self.post_number}\n"

class Orders(Base):
    __tablename__ = "Orders"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    time: Mapped[int] = mapped_column(default = time.time())
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"))
    user: Mapped["User"] = relationship(back_populates="orders")
    orderelements: Mapped[List["OrderElements"]] = relationship(back_populates="orders")

    def __repr__(self) -> str:
        dt = datetime.fromtimestamp(self.time)
        #return f"**Час замовлення:** {dt.date().year}\-{dt.date().month}\-{dt.date().day} {dt.time().hour}:{dt.time().minute}:{dt.time().second}"
        return f"*Час замовлення:* {dt.date()} {dt.time()}"

class OrderElements(Base):
    __tablename__ = "OrderElements"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    tea: Mapped[str] = mapped_column(String(30))
    weight: Mapped[int] = mapped_column()
    amount: Mapped[int] = mapped_column()
    type: Mapped[str] = mapped_column(String(30))
    order_id: Mapped[int] = mapped_column(ForeignKey("Orders.id"))
    orders: Mapped["Orders"] = relationship(back_populates="orderelements")
    
    def __repr__(self) -> str:
        return f"*Тип упаковки:* {self.type}\n*Сорт:* {self.tea}\n*Вага упаковки:* {self.weight}\n*Кількість упаковок:* {self.amount}\n*Номер замовлення:* {self.order_id}"

class Grade(Base):
    __tablename__ = "kratom_grade"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    grade: Mapped[str] = mapped_column(String(30))
    img: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(1024))
    typecosts: Mapped[List["TypeCost"]] = relationship(back_populates="grade")

class CostElement(Base):
    __tablename__ = "kratom_costelement"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    title: Mapped[str] = mapped_column(String(30))
    count: Mapped[str] = mapped_column(String(30))
    cost: Mapped[int] = mapped_column()

class TypeCost(Base):
    __tablename__ = "kratom_typecost"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    type: Mapped[str] = mapped_column(String(30))
    costelement_id: Mapped[int] = mapped_column(ForeignKey(CostElement.id))
    costelement: Mapped["CostElement"] =  relationship()
    grade_id: Mapped[int] = mapped_column(ForeignKey(Grade.id))
    grade: Mapped["Grade"] = relationship(back_populates="typecosts")

class Kratom(Base):
    __tablename__ = "kratom_variety"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    variety: Mapped[str] = mapped_column(String(30))
    img: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(1024))
    grade_id: Mapped[int] = mapped_column(ForeignKey(Grade.id))
    grade: Mapped["Grade"] = relationship()


    

    
