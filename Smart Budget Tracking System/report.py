import logging
from typing import Any, Dict
from budget_manager import BudgetManager, CURRENCY

class Report:
    @staticmethod
    def generate_report(manager: BudgetManager) -> None:
        """
        Generate and display a complete monthly budget report.
        
        Args:
            manager: BudgetManager object containing all budget data
        
        Raises:
            Exception: If there's an error generating the report
        """
        try:
            print("\n" + "=" * 55)
            print("        📊 MONTHLY BUDGET REPORT")
            print("=" * 55)
            
            remaining = manager.calculate_remaining_budget()
            
            print(f" Monthly Income    : {manager.income:.2f} {CURRENCY}")
            print(f" Total Expenses    : {manager.total_spent():.2f} {CURRENCY}")
            print(f" Remaining Budget  : {remaining:.2f} {CURRENCY}")

            print("\n" + "-" * 55)
            print(" Budget Allocation (50/30/20 Rule):")
            
            allocation = manager.allocation()
            spent = manager.spent_by_category()
            remaining = manager.remaining_by_category()
            labels = {"needs": "Needs", "wants": "Wants", "savings": "Savings"}
            
            for cat, label in labels.items():
                planned = allocation.get(cat, 0)
                used = spent.get(cat, 0)
                left = remaining.get(cat, 0)
                pct = (used / planned * 100) if planned > 0 else 0
                print(f"  {label:8} : Planned {planned:8.2f} | Used {used:8.2f} | Left {left:8.2f} | {pct:5.1f}%")

            print("\n" + "-" * 55)
            print(" Expense Details:")
            
            if not manager.expenses:
                print("  No expenses found.")
            else:
                for i, e in enumerate(sorted(manager.expenses, key=lambda x: x.amount, reverse=True), 1):
                    print("-" * 55)
                    print(f"  {i}. {e.description}")
                    print(f"      Amount   : {e.amount:.2f} {CURRENCY}")
                    print(f"      Category : {e.label()}")
                    print(f"      Date     : {e.created_at}")
                    print(f"      ID       : {e.expense_id}")

            print("\n" + "=" * 55)
            Report._show_recommendations(manager)
            print("=" * 55 + "\n")
            
            logging.info("Report generated successfully")
        except Exception as e:
            logging.error(f"Error generating report: {e}")
            raise

    @staticmethod
    def _show_recommendations(manager: BudgetManager) -> None:
        """
        Display personalized recommendations based on budget performance.
        
        Args:
            manager: BudgetManager object to analyze
        """
        print(" Recommendations:")
        
        if manager.is_on_plan():
            print("   Excellent! You're on track with your budget plan!")
        else:
            print("   You're exceeding your budget in some categories:")
            for cat, ratio in manager.usage_ratio().items():
                if ratio > 1.0:
                    label = {"needs": "Needs", "wants": "Wants", "savings": "Savings"}[cat]
                    print(f"     - {label}: {ratio*100:.1f}% over budget")

        savings_spent = manager.spent_by_category().get("savings", 0)
        savings_planned = manager.allocation().get("savings", 0)
        if savings_spent < savings_planned * 0.5:
            print("   Try to save more! You're below your savings target.")
        elif savings_spent >= savings_planned:
            print("   Great job on meeting your savings goal!")

        total = manager.total_spent()
        income = manager.income
        if income > 0 and total > income * 0.9:
            print("    You're spending more than 90% of your income. Consider cutting expenses.")
        elif total < income * 0.5:
            print("    You're spending less than 50% of your income. Keep it up!")

    @staticmethod
    def summary(manager: BudgetManager) -> Dict[str, Any]:
        """
        Return a summary dictionary of budget statistics.
        
        Args:
            manager: BudgetManager object to summarize
        
        Returns:
            Dictionary containing all budget summary statistics
        """
        return {
            "income": manager.income,
            "total_expenses": manager.total_spent(),
            "remaining": manager.calculate_remaining_budget(),
            "expenses_count": len(manager.expenses),
            "allocation": manager.allocation(),
            "spent_by_category": manager.spent_by_category(),
            "remaining_by_category": manager.remaining_by_category(),
            "on_plan": manager.is_on_plan(),
        }

    @staticmethod
    def export_report(manager: BudgetManager, filename: str = "report.txt") -> None:
        """
        Export the monthly report to a text file.
        
        Args:
            manager: BudgetManager object to export
            filename: Name of the output file (default: report.txt)
        
        Raises:
            Exception: If there's an error writing to the file
        """
        import sys
        from io import StringIO
        old = sys.stdout
        sys.stdout = StringIO()
        Report.generate_report(manager)
        out = sys.stdout.getvalue()
        sys.stdout = old
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(out)
            print(f" Report exported to {filename}")
            logging.info(f"Report exported to {filename}")
        except Exception as e:
            logging.error(f"Error exporting report: {e}")
            print(f" Error exporting report: {e}") 