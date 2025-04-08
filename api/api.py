from flask import Flask, request, jsonify, abort, send_file
import os
import json
import sqlite3
import sys
from typing import List, Dict, Any, Optional
from flask_cors import CORS
from urllib.parse import unquote

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from utils import get_db_path, get_trail_files

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Database connection helper
def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/api/trails", methods=["GET"])
def get_trails():
    """Fetch all trails from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
            SELECT t.name, t.location_lat, t.location_long, t.length,
                   d.overall_difficulty, d.cardio_intensity, d.technical_difficulty
            FROM trails t
            LEFT JOIN difficulty_ratings d ON t.trail_id = d.trail_id
        """
    )

    trails = cursor.fetchall()
    conn.close()

    result = []
    for t in trails:
        difficulty_rating = t["overall_difficulty"]
        difficulty_display = (
            str(int(difficulty_rating)) if difficulty_rating is not None else "Unknown"
        )

        result.append(
            {
                "name": t["name"],
                "location_lat": t["location_lat"],
                "location_long": t["location_long"],
                "length": t["length"],
                "difficulty": difficulty_display,
                "difficulty_rating": difficulty_rating,
                "cardio_intensity": t["cardio_intensity"],
                "technical_difficulty": t["technical_difficulty"],
            }
        )

    return result


@app.route("/api/trail_path/<trail_name>", methods=["GET"])
def get_trail_path(trail_name):
    """Retrieve trail path and details from the GeoJSON file and database."""
    decoded_name = unquote(trail_name)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT geojson_path FROM trails WHERE name = ?", (decoded_name,))
    row = cursor.fetchone()

    geojson_path = None
    if row and row["geojson_path"]:
        # Get full path from the filename stored in the database
        stored_path = row["geojson_path"]
        if os.path.isabs(stored_path):
            # For older records that might still have absolute paths
            geojson_path = stored_path
        else:
            # For newer records with just the filename
            geojson_path = os.path.join(get_trail_files(), stored_path)
    else:
        # Fallback to direct file lookup
        geojson_path = os.path.join(get_trail_files(), f"{decoded_name}.geojson")

    if not os.path.exists(geojson_path):
        print(f"File not found: {geojson_path}")
        conn.close()
        return None

    # Load GeoJSON data
    with open(geojson_path, "r") as f:
        data = json.load(f)

    coordinates = []
    for feature in data.get("features", []):
        if feature["geometry"]["type"] == "MultiLineString":
            for line in feature["geometry"]["coordinates"]:
                coordinates.extend(line)
        elif feature["geometry"]["type"] == "LineString":
            coordinates.extend(feature["geometry"]["coordinates"])

    cursor.execute(
        """
        SELECT t.trail_id, t.length, t.max_elevation, t.min_elevation,
                t.elevation_gain, t.elevation_loss 
        FROM trails t
        WHERE t.name = ?
    """,
        (decoded_name,),
    )

    trail_row = cursor.fetchone()

    difficulty = None
    if trail_row:
        trail_id = trail_row["trail_id"]

        # get difficulty ratings
        cursor.execute(
            """
            SELECT * FROM difficulty_ratings
            WHERE trail_id = ?
        """,
            (trail_id,),
        )

        diff_row = cursor.fetchone()
        if diff_row:
            difficulty = {
                "overall_difficulty": diff_row["overall_difficulty"],
                "cardio_intensity": diff_row["cardio_intensity"],
                "technical_difficulty": diff_row["technical_difficulty"],
                "accessibility": diff_row["accessibility"],
                "weather_vulnerability": diff_row["weather_vulnerability"],
            }

    conn.close()

    if trail_row:
        return {
            "name": decoded_name,
            "coordinates": coordinates,
            "length": trail_row["length"],
            "max_elevation": trail_row["max_elevation"],
            "min_elevation": trail_row["min_elevation"],
            "elevation_gain": trail_row["elevation_gain"],
            "elevation_loss": trail_row["elevation_loss"],
            "difficulty": difficulty,
        }
    else:
        return {
            "name": decoded_name,
            "coordinates": coordinates,
            "length": None,
            "max_elevation": None,
            "min_elevation": None,
            "elevation_gain": None,
            "elevation_loss": None,
        }


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": error.description}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": error.description}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal Server Error", "message": str(error)}), 500


if __name__ == "__main__":
    # Ensure the database exists
    if not os.path.exists(get_db_path()):
        print("Database not found. Please run data/init_db.py first.")
        sys.exit(1)

    # Run the Flask app
    app.run(debug=True, port=8000)
