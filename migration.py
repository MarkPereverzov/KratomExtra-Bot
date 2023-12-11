from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from classes import User,Orders,OrderElements

engine = create_engine("sqlite:///D:\\KratomUkraine-Bot\\database.db", echo=True)
User.metadata.create_all(engine)
Orders.metadata.create_all(engine)
OrderElements.metadata.create_all(engine)