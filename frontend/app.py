import json
import os
import sys
import sqlite3
from flask import Flask, render_template, jsonify, request
from urllib.parse import unquote

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/trails")
def trails():
    return render_template("trails.html")


@app.route("/trail_path/<trail_name>")
def trail_path(trail_name):
    """Render the trail path page."""
    return render_template("trail_path.html", trail_name=trail_name)


@app.route("/trailcreator")
def map_creator():
    return render_template("trail_creator.html")


UPLOAD_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "storage/user_uploads")
)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# New route to save GeoJSON
@app.route("/save_geojson", methods=["POST"])
def save_geojson():
    data = request.get_json()
    filename = data.get("filename", "default.geojson")
    geojson_data = data.get("data")

    if not filename or not geojson_data:
        return jsonify({"message": "Invalid data"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(filepath, "w") as f:
            json.dump(geojson_data, f, indent=4)
        return jsonify({"message": f"File uploaded as {filename}!"})
    except Exception as e:
        return jsonify({"message": f"Error saving file: {str(e)}"}), 500


@app.route("/upload_geojson", methods=["POST"])
def upload_geojson():
    data = request.get_json()
    filename = data.get("filename", "default.geojson")
    geojson_data = data.get("data")

    if not filename or not geojson_data:
        return jsonify({"message": "Invalid data"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(filepath, "w") as f:
            json.dump(geojson_data, f, indent=4)
        return jsonify({"message": f"GeoJSON file {filename} uploaded successfully!"})
    except Exception as e:
        return jsonify({"message": f"Error saving file: {str(e)}"}), 500


@app.route("/approve_trails")
def approve_trails():
    """Render the trail approval page."""
    user_uploads_dir = os.path.join(
        os.path.dirname(__file__), "..", "storage/user_uploads"
    )
    trails = [f for f in os.listdir(user_uploads_dir) if f.endswith(".geojson")]
    return render_template("approve_trails.html", trails=trails)


@app.route("/api/approve_trail", methods=["POST"])
def api_approve_trail():
    """Move an approved trail from user_uploads to trail_files."""
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"message": "Filename is required"}), 400

    source_path = os.path.join(
        os.path.dirname(__file__), "..", "storage/user_uploads", filename
    )
    dest_path = os.path.join(
        os.path.dirname(__file__), "..", "storage/trail_files", filename
    )

    if not os.path.exists(source_path):
        return jsonify({"message": "File not found"}), 404

    try:
        os.rename(source_path, dest_path)
        return jsonify({"message": f"{filename} approved and moved successfully!"})
    except Exception as e:
        return jsonify({"message": f"Error moving file: {str(e)}"}), 500


@app.route("/api/deny_trail", methods=["POST"])
def api_deny_trail():
    """Delete a denied trail from user_uploads."""
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"message": "Filename is required"}), 400

    file_path = os.path.join(
        os.path.dirname(__file__), "..", "storage/user_uploads", filename
    )

    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    try:
        os.remove(file_path)
        return jsonify({"message": f"{filename} has been denied and deleted."})
    except Exception as e:
        return jsonify({"message": f"Error deleting file: {str(e)}"}), 500


@app.route("/view_trail/<filename>")
def view_trail(filename):
    """Display the content of a GeoJSON trail for review."""
    file_path = os.path.join(
        os.path.dirname(__file__), "..", "storage/user_uploads", filename
    )

    if not os.path.exists(file_path):
        return "Trail not found", 404

    with open(file_path, "r") as f:
        geojson_data = json.load(f)

    return render_template(
        "view_trail.html", trail_data=geojson_data, filename=filename
    )


if __name__ == "__main__":
    app.run(debug=True)
