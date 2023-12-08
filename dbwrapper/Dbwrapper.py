import sqlite3
from classes import User

class Dbwrapper:
    def __init__(self,connectionstr):
        self.connectionstr = connectionstr
    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.connectionstr)
    def getAllUsers(self):
        con = self.connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM Users")
        users = cur.fetchall()
        con.close()
        return users
    def getUser(self,dict):
        con = self.connect()
        cur = con.cursor()
        exstr = f"SELECT * FROM Users WHERE "
        for key in dict:
            exstr += f"{key}={dict[key]} "
        cur.execute(exstr)
        tmp = cur.fetchone()
        con.close()
        user = User.User(tmp[1],tmp[2],tmp[3],tmp[4],tmp[5],"Відділення",tmp[6])
        return user