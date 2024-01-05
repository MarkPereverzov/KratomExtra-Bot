from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from classes import Kratom,Grade,CostElement,TypeCost,User,Orders,OrderElements,CostOrderElement

engine = create_engine("sqlite:///D:\\KratomUkraine-Bot\\kratom.db", echo=True)


User.metadata.create_all(engine)
Orders.metadata.create_all(engine)
OrderElements.metadata.create_all(engine)
Kratom.metadata.create_all(engine)
Grade.metadata.create_all(engine)
TypeCost.metadata.create_all(engine)
CostElement.metadata.create_all(engine)
CostOrderElement.metadata.create_all(engine)

while True:
    ch = input("Enter Table: ")

    if ch == "kratom":
        variety = input("Enter variety: ")
        img = input("Enter name of img file: ")
        description = input("Enter description: ")
        grade_id = int(input("Enter grade id: "))

        with Session(engine) as session:
            session.add(Kratom(variety=variety,img=img,description=description,grade_id=grade_id))
            session.commit()

    elif ch == "grade":
        grade = input("Enter grade: ")
        img = input("Enter name of img file: ")
        description = input("Enter description: ")

        with Session(engine) as session:
            session.add(Grade(grade=grade,img=img,description=description))
            session.commit()

    elif ch == "typecost":
        type = input("Enter type: ")
        grade_id = int(input("Enter grade_id: "))
        costelement_id = int(input("Enter costelement_id: "))

        with Session(engine) as session:
            session.add(TypeCost(type=type,grade_id=grade_id,costelement_id=costelement_id))
            session.commit()

    elif ch == "costelement":
        title = input("Enter title: ")
        cost = int(input("Enter cost: "))
        count = input("Enter count: ")

        with Session(engine) as session:
            session.add(CostElement(title=title,cost=cost,count=count))
            session.commit()

    stopw = input("Add Kratom ? (0 for Exit) ")
    if stopw == "0": 
        break
