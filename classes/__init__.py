from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
import time

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
        return f"**Час замовлення:** {self.time}"

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
        return f"**Сорт:** {self.tea}\n**Вага упаковки:** {self.weight}\n**Кількість упаковок:** {self.amount}\n**Номер замовлення:** {self.orderid}"