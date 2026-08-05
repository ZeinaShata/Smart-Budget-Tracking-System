import logging
from budget_manager import BudgetManager, BudgetError
from report import Report
from file_handler import FileHandler

def menu():
    print("\n" + "=" * 45)
    print("   Smart Budget Tracking System")
    print("=" * 45)
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Search Expense")
    print("4. Update Expense")
    print("5. Delete Expense")
    print("6. Remaining Budget")
    print("7. Monthly Report")
    print("8. Save Data")
    print("9. Load Data")
    print("0. Exit")
    print("=" * 45)

def main():
    logging.info("=== Application Started ===")
    print("Welcome to Smart Budget Tracking System")
    
    while True:
        try:
            income = float(input("Enter your monthly income: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    manager = BudgetManager(income)
    logging.info(f"User set income: {income}")
    
    while True:
        menu()
        choice = input("Choose: ")
        
        if choice == "1":
            try:
                amount = float(input("Amount: "))
                category = input("Category (needs/wants/savings): ").lower()
                description = input("Description: ")
                manager.add_expense(amount, category, description)
                print("Expense added successfully.")
            except BudgetError as e:
                print(f"Error: {e}")
                
        elif choice == "2":
            print(manager.view_expenses())
            
        elif choice == "3":
            keyword = input("Search keyword: ")
            result = manager.search_expense(keyword)
            if result:
                for expense in result:
                    print(expense)
            else:
                print("No expenses found.")
                
        elif choice == "4":
            try:
                expense_id = int(input("Expense ID: "))
                amount = input("New Amount (Press Enter to skip): ")
                category = input("New Category (Press Enter to skip): ")
                description = input("New Description (Press Enter to skip): ")
                manager.update_expense(
                    expense_id,
                    amount=float(amount) if amount else None,
                    category=category if category else None,
                    description=description if description else None
                )
                print("Expense updated successfully.")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == "5":
            try:
                expense_id = int(input("Expense ID: "))
                manager.delete_expense(expense_id)
                print("Expense deleted successfully.")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == "6":
            print(f"\nRemaining Budget: {manager.calculate_remaining_budget()} جنيه")
            print("\nRemaining By Category:")
            for category, value in manager.remaining_by_category().items():
                print(f"  {category}: {value}")
                
        elif choice == "7":
            Report.generate_report(manager)
            
        elif choice == "8":
            try:
                FileHandler.save_data(manager.to_dict())
                print("Data saved successfully.")
            except Exception as e:
                print(f"Error saving data: {e}")
                
        elif choice == "9":
            data = FileHandler.load_data()
            if data:
                try:
                    manager.load_dict(data)
                    print("Data loaded successfully.")
                except Exception as e:
                    print(f"Error loading data: {e}")
            else:
                print("No data found or file is empty.")
                
        elif choice == "0":
            try:
                FileHandler.save_data(manager.to_dict())
                print("Thank you for using Smart Budget Tracking System.")
                logging.info("=== Application Ended ===")
            except Exception as e:
                print(f"Error saving data: {e}")
            break
            
        else:
            print("Invalid Choice. Try Again.")

if __name__ == "__main__":
    main()