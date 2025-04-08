import os
import glob

"""
run this from main directory using py -m storage.js_to_geojson
"""

# Set the directory where the .js files are located
directory = "./storage/trail_files"  # Change this if needed

# Find all .js files in the directory
print("Finding .js files...")
js_files = glob.glob(os.path.join(directory, "*.js"))

# Rename each .js file to .geojson
for js_file in js_files:
    geojson_file = js_file.rsplit(".", 1)[0] + ".geojson"

    if os.path.exists(geojson_file):
        # If .geojson already exists, delete the .js file
        os.remove(js_file)
        print(f"Deleted: {js_file} (since {geojson_file} already exists)")
    else:
        # Rename .js to .geojson
        os.rename(js_file, geojson_file)
        print(f"Renamed: {js_file} -> {geojson_file}")

print("Renaming complete!")
