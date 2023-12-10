import sqlite3
from classes import User
from classes import Orders
from classes import OrderElements


class Dbwrapper:
    def __init__(self,connectionstr):
        self.connectionstr = connectionstr

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.connectionstr)
    
    def getAllUsers(self) -> [User.User]:
        con = self.connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM Users")
        usersstr = cur.fetchall()
        users = []
        for userstr in usersstr:
            user = User.User(userstr[1],userstr[2],userstr[3],userstr[4],userstr[5],userstr[6],userstr[7])
            user.id = userstr[0]
            users.append(user)
        con.close()
        return users
    
    def getUser(self,dict) -> User.User:
        con = self.connect()
        cur = con.cursor()
        exstr = f"SELECT * FROM Users WHERE "
        for key in dict:
            exstr += f"{key}={dict[key]} "
        cur.execute(exstr)
        tmp = cur.fetchone()
        con.close()
        if tmp == None:
            user = None
        else: 
            user = User.User(tmp[1],tmp[2],tmp[3],tmp[4],tmp[5],tmp[6],tmp[7])
            user.id = tmp[0]
        return user
    #PEREDELAT
    def getUserWithOrders(self,dict) -> User.User:
        con = self.connect()
        cur = con.cursor()
        exstr = f"SELECT * FROM Users JOIN Orders ON Users.ID = Orders.UserId JOIN OrderElements ON Orders.ID = OrderElemnts.OrderID"
        exstr += " WHERE "
        for key in dict:
            exstr += f"{key}={dict[key]} "
        cur.execute(exstr)
        tmp = cur.fetchone()
        con.close()
        if tmp == None:
            user = None
        else:
            user = User.User(tmp[1],tmp[2],tmp[3],tmp[4],tmp[5],tmp[6],tmp[7])
            user.id = tmp[0]
            order = Orders.Orders(tmp[9],tmp[10])
            order.id = tmp[8]
            order.orderelements = OrderElements.OrderElements(tmp[12],tmp[13].tmp[14],tmp[15])
            order.orderelements.id = tmp[11]
            user.orders.append(order)
        return user

    def saveUser(self,user):
        con = self.connect()
        cur = con.cursor()
        exstr = f"INSERT INTO Users (UserId,FirstName,SecondName,PhoneNumber,City,PostType,PostNumber) VALUES ({user.userid},'{user.name}','{user.surname}','{user.phone}','{user.city}','{user.post_type}',{user.post_number});"
        print(exstr)
        cur.execute(exstr)
        con.commit()
        con.close()

    def updateUser(self,user):
        con = self.connect()
        cur = con.cursor()
        exstr = f"UPDATE Users SET FirstName='{user.name}', SecondName='{user.surname}',PhoneNumber='{user.phone}',City='{user.city}',PostType='{user.post_type}',PostNumber={user.post_number} WHERE UserId={user.userid};"
        cur.execute(exstr)
        con.commit()
        con.close()
    #PEREDELAT
    def getAllOrders(self) -> [Orders.Orders]:
        con = self.connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM Orders JOIN OrderElements ON Orders.ID = OrderElemnts.OrderID")
        ordersstr = cur.fetchall()
        orders = []
        for orderstr in ordersstr:
            tmp = Orders.Orders(orderstr[1],orderstr[2])
            tmp.id = orderstr[0]
            oes = OrderElements.OrderElements(orderstr[4],orderstr[5],orderstr[6],orderstr[7])
            oes.id = orderstr[3]
            tmp.orderelements.append(oes)
            orders.append(tmp)
        con.close()
        return orders
    
    def getOrders(self,dict) -> Orders.Orders:
        con = self.connect()
        cur = con.cursor()
        exstr = f"SELECT * FROM Orders "
        exstr += "LEFT JOIN OrderElements ON Orders.ID = OrderElements.OrderID "
        exstr += "WHERE "
        for key in dict:
            exstr += f"{key}={dict[key]} "
        cur.execute(exstr)
        print(exstr)
        tmp = cur.fetchone()
        con.close()
        if tmp == None:
            order = None
        else:
            order = Orders.Orders(tmp[1],tmp[2])
            order.id = tmp[0]
            oes = OrderElements.OrderElements(tmp[4],tmp[5],tmp[6],tmp[7])
            oes.id = tmp[3]
            order.orderelements.append(oes)
        return order
    
    def saveOrders(self,orders):
        con = self.connect()
        cur = con.cursor()
        exstr = f"INSERT INTO Orders (OrderTime,UserId) VALUES ({orders.time},{orders.userid});"
        print(exstr)
        cur.execute(exstr)
        con.commit()
        con.close()
    
    def saveOrderElements(self,orderelements):
        con = self.connect()
        cur = con.cursor()
        exstr = f"INSERT INTO OrderElements (Tea,Weight,Amount,OrderID) VALUES ('{orderelements.tea}','{orderelements.weight}',{orderelements.amount},{orderelements.orderid});"
        print(exstr)
        cur.execute(exstr)
        con.commit()
        con.close()

    def updateOrderElements(self,orderelements):
        con = self.connect()
        cur = con.cursor()
        exstr = f"UPDATE OrderElements SET Tea='{orderelements.tea}',Weight={orderelements.weight},Amount={orderelements.amount},OrderID={orderelements.orderid});"
        print(exstr)
        cur.execute(exstr)
        con.commit()
        con.close()
    
    def deleteOrderElements(self,id):
        con = self.connect()
        cur = con.cursor()
        exstr = f"DELETE FROM OrderElements WHERE ID={id});"
        print(exstr)
        cur.execute(exstr)
        con.commit()
        con.close()

    def deleteOrders(self,id):
        con = self.connect()
        cur = con.cursor()
        exstr = f"DELETE FROM Orders WHERE ID={id});"
        print(exstr)
        cur.execute(exstr)
        con.commit()
        con.close()
