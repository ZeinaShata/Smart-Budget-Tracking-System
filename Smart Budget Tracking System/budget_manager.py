import logging
from dataclasses import dataclass, field, asdict
from datetime import date
from functools import reduce
from typing import Any, Optional

logging.basicConfig(
    filename='budget.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

CATEGORIES = ("needs", "wants", "savings")
VALID_CATEGORIES = set(CATEGORIES)
CATEGORY_LABELS = {"needs": "Needs", "wants": "Wants", "savings": "Savings"}
SPLIT = {"needs": 0.50, "wants": 0.30, "savings": 0.20}
CURRENCY = "EGP"

class BudgetError(Exception):
    def __init__(self, message="Budget Manager Error"):
        self.message = message
        super().__init__(self.message)
        logging.error(f"BudgetError: {message}")

class InvalidAmountError(BudgetError):
    def __init__(self, value):
        msg = f"Invalid amount: {value!r}. Must be > 0."
        super().__init__(msg)
        self.value = value

class InvalidCategoryError(BudgetError):
    def __init__(self, category):
        msg = f"Invalid category: {category!r}. Allowed: needs/wants/savings."
        super().__init__(msg)
        self.category = category

class ExpenseNotFoundError(BudgetError):
    def __init__(self, expense_id):
        msg = f"Expense with ID {expense_id} not found."
        super().__init__(msg)
        self.expense_id = expense_id

@dataclass(repr=False)
class Expense:
    expense_id: int
    amount: float
    category: str
    description: str = ""
    created_at: str = field(default_factory=lambda: date.today().isoformat())

    def label(self):
        return CATEGORY_LABELS.get(self.category, self.category)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            expense_id=int(data["expense_id"]),
            amount=float(data["amount"]),
            category=str(data["category"]),
            description=str(data.get("description", "")),
            created_at=str(data.get("created_at", date.today().isoformat())),
        )

    def __repr__(self):
        return f"Expense(id={self.expense_id}, amount={self.amount:.2f}, category={self.category!r}, description={self.description!r})"

def validate_amount(value):
    try:
        amount = float(value)
    except (TypeError, ValueError) as e:
        logging.warning(f"Invalid amount attempt: {value}")
        raise InvalidAmountError(value) from e
    if amount <= 0:
        logging.warning(f"Amount <= 0: {value}")
        raise InvalidAmountError(value)
    return round(amount, 2)

def validate_category(value):
    category = str(value).strip().lower()
    if category not in VALID_CATEGORIES:
        logging.warning(f"Invalid category attempt: {value}")
        raise InvalidCategoryError(value)
    return category

class BudgetManager:
    def __init__(self, income=0.0):
        self.income = float(income)
        self.expenses = []
        self._next_id = 1
        logging.info(f"BudgetManager created with income: {income}")

    def add_expense(self, amount, category, description=""):
        try:
            expense = Expense(
                expense_id=self._next_id,
                amount=validate_amount(amount),
                category=validate_category(category),
                description=str(description).strip()[:100],
            )
            self.expenses.append(expense)
            self._next_id += 1
            logging.info(f"Expense added: {expense}")
            return expense
        except BudgetError as e:
            logging.error(f"Failed to add expense: {e}")
            raise

    def delete_expense(self, expense_id):
        try:
            target = None
            for expense in self.expenses:
                if expense.expense_id == int(expense_id):
                    target = expense
                    break
            if target is None:
                raise ExpenseNotFoundError(int(expense_id))
            self.expenses.remove(target)
            logging.info(f"Expense deleted: {target}")
            return target
        except BudgetError as e:
            logging.error(f"Failed to delete expense: {e}")
            raise

    def update_expense(self, expense_id, amount=None, category=None, description=None):
        try:
            expense = self.get_expense(expense_id)
            if amount is not None:
                expense.amount = validate_amount(amount)
            if category is not None:
                expense.category = validate_category(category)
            if description is not None:
                expense.description = str(description).strip()[:100]
            logging.info(f"Expense updated: {expense}")
            return expense
        except BudgetError as e:
            logging.error(f"Failed to update expense: {e}")
            raise

    def get_expense(self, expense_id):
        for expense in self.expenses:
            if expense.expense_id == int(expense_id):
                return expense
        raise ExpenseNotFoundError(int(expense_id))

    def search_expense(self, keyword="", category=None, min_amount=None, max_amount=None):
        keyword = str(keyword).strip().lower()
        results = [
            e for e in self.expenses
            if keyword in e.description.lower() or keyword in e.category or keyword in e.label()
        ]
        if category:
            category = validate_category(category)
            results = list(filter(lambda x: x.category == category, results))
        if min_amount is not None:
            results = [e for e in results if e.amount >= float(min_amount)]
        if max_amount is not None:
            results = [e for e in results if e.amount <= float(max_amount)]
        return sorted(results, key=lambda x: x.amount, reverse=True)

    def view_expenses(self, category=None):
        items = self.expenses if not category else list(filter(lambda x: x.category == validate_category(category), self.expenses))
        if not items:
            return "No expenses found."
        lines = ["-" * 75]
        lines.append(f"{'#':<3} {'ID':<4} {'Date':<12} {'Category':<12} {'Amount':>10}  Description")
        lines.append("-" * 75)
        for i, e in enumerate(items, 1):
            lines.append(f"{i:<3} {e.expense_id:<4} {e.created_at:<12} {e.label():<12} {e.amount:>10.2f}  {e.description}")
        lines.append("-" * 75)
        lines.append(f"Total: {self.total_spent():.2f} {CURRENCY} | Expenses: {len(items)}")
        lines.append("-" * 75)
        return "\n".join(lines)

    def calculate_remaining_budget(self):
        return round(self.income - self.total_spent(), 2)

    def remaining_by_category(self):
        plan = self.allocation()
        spent = self.spent_by_category()
        return {name: round(plan[name] - spent[name], 2) for name in CATEGORIES}

    def set_income(self, income):
        self.income = validate_amount(income)
        logging.info(f"Income updated to: {income}")
        return self.income

    def allocation(self):
        return {name: round(self.income * ratio, 2) for name, ratio in SPLIT.items()}

    def total_spent(self):
        return round(reduce(lambda a, b: a + b, map(lambda x: x.amount, self.expenses), 0.0), 2)

    def spent_by_category(self):
        totals = {name: 0.0 for name in CATEGORIES}
        for e in self.expenses:
            totals[e.category] += e.amount
        return {name: round(value, 2) for name, value in totals.items()}

    def usage_ratio(self):
        plan = self.allocation()
        spent = self.spent_by_category()
        return {name: round(spent[name] / plan[name], 4) if plan[name] > 0 else 0.0 for name in CATEGORIES}

    def is_on_plan(self):
        return all(r <= 1.0 for r in self.usage_ratio().values())

    def to_dict(self):
        return {"income": self.income, "next_id": self._next_id, "expenses": [e.to_dict() for e in self.expenses]}

    def load_dict(self, data):
        try:
            self.income = float(data.get("income", 0.0))
            self.expenses = [Expense.from_dict(e) for e in data.get("expenses", [])]
            self._next_id = int(data.get("next_id", len(self.expenses) + 1))
            logging.info(f"Data loaded: {len(self.expenses)} expenses")
        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            raise

    def __repr__(self):
        return f"BudgetManager(income={self.income:.2f}, expenses={len(self.expenses)}, remaining={self.calculate_remaining_budget():.2f})"

    def __len__(self):
        return len(self.expenses)