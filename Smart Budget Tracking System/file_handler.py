import json
import logging
from typing import Any, Dict, Optional


class FileHandler:
    @staticmethod
    def save_data(data: Dict[str, Any], filename: str = "data.json") -> None:
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data: {e}")
            raise IOError(f"Error saving data: {e}")

    @staticmethod
    def load_data(filename: str = "data.json") -> Optional[Dict[str, Any]]:
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
            
