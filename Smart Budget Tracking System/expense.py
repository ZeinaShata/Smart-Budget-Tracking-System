class Expense:
    def __init__(self, name, amount, category, date):
        self.name = name
        self.amount = amount
        self.category = category
        self.date = date

    def __repr__(self):
        return (f"Expense(Name: {self.name}, "
                f"Amount: {self.amount}, "
                f"Category: {self.category}, "
                f"Date: {self.date})")