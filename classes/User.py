class User:
    def __init__(self,userid,name,surname,phone,city,post_type,post_number):
        self.userid = userid
        self.name = name
        self.surname = surname
        self.phone = phone
        self.city = city
        self.post_type = post_type
        self.post_number = post_number
        self.orders = []
        self.id = id

    def __repr__(self) -> str:
        return f"Ім'я: {self.name}\nПрізвище: {self.surname}\n"+f"Телефон: {self.phone}\nМісто: {self.city}\n"+f"Почтомат/відділення: {self.post_type}\n"+f"Номер почтомату/відділення: {self.post_number}\n"
