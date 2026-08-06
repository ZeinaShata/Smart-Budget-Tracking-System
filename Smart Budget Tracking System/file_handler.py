import json
import logging
from typing import Any, Dict, List, Optional

class FileHandler:
    @staticmethod
    def save_data(data: Dict[str, Any], filename: str = "data.json") -> None:
        """
        Save budget data to a JSON file.
        
        Args:
            data: Dictionary containing budget data (income, expenses, etc.)
            filename: Name of the JSON file to save to (default: data.json)
        
        Raises:
            IOError: If there's an error writing to the file
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data: {e}")
            raise IOError(f"Error saving data: {e}")

    @staticmethod
    def load_data(filename: str = "data.json") -> Optional[Dict[str, Any]]:
        """
        Load budget data from a JSON file.
        
        Args:
            filename: Name of the JSON file to load from (default: data.json)
        
        Returns:
            Dictionary containing budget data if successful, None if file not found or invalid
        
        Raises:
            IOError: If there's an error reading the file
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "income" in data and "expenses" in data:
                    logging.info(f"Data loaded from {filename}")
                    return data
                logging.warning(f"Invalid data format in {filename}")
                return None
        except FileNotFoundError:
            logging.warning(f"File {filename} not found")
            return None
        except json.JSONDecodeError:
            logging.warning(f"Invalid JSON in {filename}")
            return None
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            return None

        import csv
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["ID", "Amount", "Category", "Description", "Date"])
                for e in expenses:
                    w.writerow([e.expense_id, e.amount, e.category, e.description, e.created_at])
            logging.info(f"Data exported to {filename}")
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            raise IOError(f"Error exporting to CSV: {e}")
