import json
import sys
import os

import sqlite3

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from utils import get_db_path

"""
This file creates the database
doesn't need to be ran again since the database already exists
"""


def main():

    print("Initializing SQLite Database...")

    conn = sqlite3.connect(get_db_path())  # creates/opens a database file
    cursor = conn.cursor()  # cursor is used to use SQL commands

    # Create tables
    cursor.executescript(
        """
    CREATE TABLE trails (
        trail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        location_lat REAL,
        location_long REAL,
        length REAL,
        elevation_gain REAL,
        elevation_loss REAL,
        max_elevation REAL,
        min_elevation REAL,
        geojson_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE trail_segments (
        segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trail_id INTEGER,
        segment_order INTEGER,
        start_lat REAL,
        start_long REAL,
        end_lat REAL,
        end_long REAL,
        length REAL,
        elevation_gain REAL,
        elevation_loss REAL,
        avg_slope REAL,
        max_slope REAL,
        terrain_type TEXT,
        FOREIGN KEY (trail_id) REFERENCES trails(trail_id) ON DELETE CASCADE
    );

    CREATE TABLE difficulty_ratings (
        rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trail_id INTEGER,
        cardio_intensity REAL,
        technical_difficulty REAL,
        accessibility REAL,
        weather_vulnerability REAL,
        overall_difficulty REAL,
        FOREIGN KEY (trail_id) REFERENCES trails(trail_id) ON DELETE CASCADE
    );

    CREATE TABLE terrain_data (
        tdata_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trail_id INTEGER,
        surface_type TEXT,
        shade_percentage REAL,
        water_crossings TEXT,
        exposure_level REAL,
        FOREIGN KEY (trail_id) REFERENCES trails(trail_id) ON DELETE CASCADE
    );

    CREATE TABLE trail_notes (
        note_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trail_id INTEGER,
        note_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (trail_id) REFERENCES trails(trail_id) ON DELETE CASCADE
    );
    """
    )

    # Commit changes and close connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
