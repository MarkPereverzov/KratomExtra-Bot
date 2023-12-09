class Orders:
    def __init__(self,time,userid):
        self.time = time
        self.userid = userid
        self.orderelements = []
        
    def __repr__(self) -> str:
        return f"**Час замовлення:** {self.time}"