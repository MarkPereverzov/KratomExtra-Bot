from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
from classes import Orders 
import time

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    userid: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    surname: Mapped[str] = mapped_column(String(30))
    phone: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(30))
    post_type: Mapped[str] = mapped_column(String(30))
    post_number: Mapped[int] = mapped_column()
    orders: Mapped[List["Orders"]] = relationship(back_populates="User")

    # def __init__(self,userid,name,surname,phone,city,post_type,post_number):
    #     self.userid = userid
    #     self.name = name
    #     self.surname = surname
    #     self.phone = phone
    #     self.city = city
    #     self.post_type = post_type
    #     self.post_number = post_number
    #     self.orders = []
    #     self.id = 0

    def __repr__(self) -> str:
        return f"Ім'я: {self.name}\nПрізвище: {self.surname}\n"+f"Телефон: {self.phone}\nМісто: {self.city}\n"+f"Почтомат/відділення: {self.post_type}\n"+f"Номер почтомату/відділення: {self.post_number}\n"

class Orders(Base):
    __tablename__ = "Orders"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    time: Mapped[int] = mapped_column(default = time.time())
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"))
    orderelements: Mapped[List["OrderElements"]] = relationship(back_populates="Orders")

    # def __init__(self,time,userid):
    #     self.time = time
    #     self.userid = userid
    #     self.orderelements = []
    #     self.id = 0
    def __repr__(self) -> str:
        return f"**Час замовлення:** {self.time}"

class OrderElements(Base):
    __tablename__ = "OrderElements"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    tea: Mapped[str] = mapped_column(String(30))
    weight: Mapped[int] = mapped_column()
    amount: Mapped[int] = mapped_column()
    type: Mapped[str] = mapped_column(String(30))
    order_id: Mapped[int] = mapped_column(ForeignKey("Orders.id"))

    # def __init__(self,tea,weight,amount,orderid):
    #     self.tea = tea
    #     self.weight = weight
    #     self.amount = amount
    #     self.orderid = orderid
    #     self.id = 0

    def __repr__(self) -> str:
        return f"**Сорт:** {self.tea}\n**Вага упаковки:** {self.weight}\n**Кількість упаковок:** {self.amount}\n**Номер замовлення:** {self.orderid}"