from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
from classes.User import User
from classes.Orders import Orders

class Base(DeclarativeBase):
    pass

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