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
            users.append(User.User(userstr[0],userstr[2],userstr[3],userstr[4],userstr[5],userstr[6],userstr[7]))
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
        user = None if tmp == None else User.User(tmp[0],tmp[2],tmp[3],tmp[4],tmp[5],tmp[6],tmp[7])
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

    def getAllOrders(self) -> [Orders.Orders]:
        con = self.connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM Orders")
        ordersstr = cur.fetchall()
        orders = []
        for orderstr in ordersstr:
            orders.append(Orders.Orders(orderstr[1]))
        con.close()
        return users