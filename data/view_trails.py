import os
import sys
import sqlite3

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from utils import get_db_path


def view_trails():
    """Fetches and prints all trails from the database."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trails")
    trails = cursor.fetchall()

    if not trails:
        print("No trails found in the database.")
    else:
        print("\nAll Trails in Database:")
        print("-" * 80)
        for trail in trails:
            (
                trail_id,
                name,
                loc_lat,
                loc_long,
                length,
                elevation_gain,
                elevation_loss,
                max_elevation,
                min_elevation,
                geojson_path,
                created_at,
            ) = trail
            print(f"Trail ID: {trail_id}")
            print(f"Name: {name}")
            print(f"Location: ({loc_lat}, {loc_long})")
            print(f"Length: {length} km")
            print(
                f"Elevation Gain: {elevation_gain} m, Elevation Loss: {elevation_loss} m"
            )
            print(f"Max Elevation: {max_elevation} m, Min Elevation: {min_elevation} m")
            print(f"GeoJSON Path: {geojson_path}")
            print(f"Created At: {created_at}")
            print("-" * 80)

    conn.close()


if __name__ == "__main__":
    view_trails()
