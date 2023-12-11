from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
from classes.Orders import Orders 

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    userid: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    surname: Mapped[str] = mapped_column(String(30))
    phone: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(30))
    post_type: Mapped[str] = mapped_column(String(30))
    post_number: Mapped[int] = mapped_column()
    orders: Mapped[List["Orders"]] = relationship(backref="Users", cascade="all, delete-orphan")

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
