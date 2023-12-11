from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
from classes.User import User
from classes.OrderElements import OrderElements

class Base(DeclarativeBase):
    pass

class Orders(Base):
    __tablename__ = "Orders"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    time: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    orderelements: Mapped[List["OrderElements"]] = relationship(backref="Orders", cascade="all, delete-orphan")

    # def __init__(self,time,userid):
    #     self.time = time
    #     self.userid = userid
    #     self.orderelements = []
    #     self.id = 0
    def __repr__(self) -> str:
        return f"**Час замовлення:** {self.time}"