class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role


class FoodItem:
    def __init__(self, name, quantity, status="available"):
        self.name = name
        self.quantity = quantity
        self.status = status
