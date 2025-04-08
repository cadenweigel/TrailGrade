import json
import sys
import os
import sqlite3
from datetime import datetime

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from utils import get_db_path, get_trail_files
from core.trail import Trail

"""
run using py -m data.add_trails
-m runs from root directory
"""


def get_trails(directory=None):
    """Returns a list of all .geojson files in the specified directory with full paths."""
    if directory is None:
        directory = get_trail_files()

    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist.")

    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".geojson")
    ]


def main():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    trail_paths = get_trails()
    trails = []

    for filepath in trail_paths:
        trails.append(Trail(filepath))

    for t in trails:
        name = t.name  # get map name
        path = t.file  # get path

        # Check if trail already exists - look for basename only
        basename = os.path.basename(path)
        cursor.execute(
            "SELECT 1 FROM trails WHERE geojson_path = ? OR geojson_path = ?",
            (basename, path),
        )
        exists = cursor.fetchone()

        if not exists:
            # use save_to_database to store all trail data including difficulty ratings
            t.save_to_database(conn)
            print(f"Added trail: {name}, Length: {t.length:.2f} km")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
