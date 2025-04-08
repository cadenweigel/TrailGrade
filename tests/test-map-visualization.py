import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from core.trail import Trail

# Path to the GeoJSON file you want to visualize
trail_path = os.path.join(
    project_root, "storage", "trail_files", "Pre's Trail.geojson"
)  # Change this to any trail file

# Create a Trail object
trail = Trail(filepath=trail_path)

# Print basic trail information
print(trail)

# Generate and display an interactive map
map_file = trail.get_trail_as_map(include_segments=True, include_difficulty=True)
print(f"Map visualization saved to: {map_file}")

# You can also get detailed analysis
analysis = trail.analyze_trail()
print("\nTrail Analysis:")
for key, value in analysis.items():
    if key == "difficulty_ratings":
        print(f"\n{key}:")
        for rating_key, rating_value in value.items():
            print(f"  {rating_key}: {rating_value}")
    else:
        print(f"{key}: {value}")
