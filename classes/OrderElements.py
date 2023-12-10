class OrderElements:
    def __init__(self,tea,weight,amount,orderid):
        self.tea = tea
        self.weight = weight
        self.amount = amount
        self.orderid = orderid
        self.id = 0
    def __repr__(self) -> str:
        return f"**Сорт:** {self.tea}\n**Вага упаковки:** {self.weight}\n**Кількість упаковок:** {self.amount}\n**Номер замовлення:** {self.orderid}"