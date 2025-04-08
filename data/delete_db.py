import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from utils import get_db_path


def delete_sqlite_db(db_path):
    """Deletes the specified SQLite database file."""
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Database '{db_path}' has been deleted successfully.")
        except Exception as e:
            print(f"Error deleting the database: {e}")
    else:
        print(f"Database '{db_path}' does not exist.")


# usage
db_file = get_db_path()
delete_sqlite_db(db_file)
