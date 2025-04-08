# built in libraries
import json
import math
import os
from typing import List, Tuple, Dict, Optional, Any
import statistics
import sqlite3

# third-party libraries
import geopandas as gpd
import folium

# internal imports
from .point import Point
from .analysis import TrailAnalyzer
from .segment import TrailSegment


class Trail:
    """Enhanced Trail class with analysis capabilities"""

    def __init__(
        self,
        filepath: str,
        segment_length: float = 0.5,
        analyzer: Optional["TrailAnalyzer"] = None,
    ) -> None:
        # store original path (might be full path or just filename)
        self.file = filepath

        # if it's not an absolute path, assume its a filename in the trail_files dir
        if not os.path.isabs(filepath):
            from utils import get_trail_files

            full_path = os.path.join(get_trail_files(), filepath)
        else:
            full_path = filepath

        # basic trail data
        self.name = self.get_map_name()
        self.segment_length = segment_length

        # GeoDataFrame Related Functions
        self.gdf = gpd.read_file(
            filepath
        )  # this gets initialized since it's used a lot

        # extract points from GeoJSON
        self.points = self.extract_points()

        # calculate basic metrics
        self.length = self.calculate_trail_length()
        self.elevation_gain, self.elevation_loss = self.calculate_elevation_up_down()
        self.max_elevation = self.calculate_max_elevation()
        self.min_elevation = self.calculate_min_elevation()
        self.elevation_variance = self.calculate_elevation_variance()
        self.avg_slope = self.calculate_avg_slope()
        self.max_slope = self.calculate_max_slope()

        # segment the trail
        self.segments = self.create_segments()

        # analyzer for difficulty ratings
        self.analyzer = analyzer if analyzer else TrailAnalyzer()

    def __str__(self) -> str:
        return (
            f"Trail: {self.name}\n"
            f"Length: {self.length:.2f} km\n"
            f"Elevation Gain: {self.elevation_gain:.1f} m\n"
            f"Elevation Loss: {self.elevation_loss:.1f} m\n"
            f"Elevation Range: {self.min_elevation:.1f} - {self.max_elevation:.1f} m\n"
            f"Avg Slope: {self.avg_slope:.1f}%\n"
            f"Max Slope: {self.max_slope:.1f}%"
        )

    def get_map_name(self) -> str:
        """Extracts map name from filename (without extension)."""
        return os.path.splitext(os.path.basename(self.file))[0]

    def get_location_coordinates(self) -> Tuple[float, float]:
        """Get location from metadata or estimate from coordinates"""
        # would be enhanced with geocoding in full implementation
        center = self.find_center()
        return center[0], center[1]

    def find_center(self) -> list[float]:
        """opens a file and finds the latitude and longitude of the center of all data points"""
        gdf_projected = self.gdf.to_crs(
            epsg=3857
        )  # Convert to a projected CRS (e.g., EPSG:3857 for Web Mercator)
        centroid = (
            gdf_projected.geometry.centroid
        )  # Compute the centroid in projected CRS
        centroid_latlon = centroid.to_crs(
            epsg=4326
        )  # Convert back to latitude/longitude
        return [
            float(centroid_latlon.y.mean()),
            float(centroid_latlon.x.mean()),
        ]  # return latitude and longitude

    def calculate_zoom(self) -> int:
        """Calculate an appropriate zoom level based on dataset extent."""
        minx, miny, maxx, maxy = self.gdf.total_bounds  # Bounding box
        lat_diff = maxy - miny
        lon_diff = maxx - minx
        zoom = max(
            1, int(12 - math.log2(max(lat_diff, lon_diff) + 1e-6))
        )  # Basic zoom level logic (adjust as needed)
        return zoom

    def get_trail_as_map(
        self, include_segments: bool = True, include_difficulty: bool = True
    ) -> str:
        """Uses the folium library to create an HTML map visualization"""
        # get values needed for map
        map_center = self.find_center()
        zoom = self.calculate_zoom()

        # create map
        map = folium.Map(location=map_center, zoom_start=zoom)

        # ensure we have the full path
        if not os.path.isabs(self.file):
            from utils import get_trail_files

            full_path = os.path.join(get_trail_files(), self.file)
        else:
            full_path = self.file

        # add the basic trail
        folium.GeoJson(
            self.file,
            name=self.name,
            style_function=lambda x: {"color": "blue", "weight": 3},
        ).add_to(map)

        # add points for elevation visualization (optional)
        if include_difficulty:
            for point in self.points[::10]:  # sample points for readability
                folium.CircleMarker(
                    location=[point.latitude, point.longitude],
                    radius=3,
                    color="green",
                    fill=True,
                    popup=f"Elevation: {point.elevation:.1f}m",
                ).add_to(map)

        # add segment visualization
        if include_segments and self.segments:
            for segment in self.segments:
                # color based on slope
                slope = segment.avg_slope
                if slope > 15:
                    color = "red"
                elif slope > 8:
                    color = "orange"
                else:
                    color = "green"

                # draw segment line
                points = [[p.latitude, p.longitude] for p in segment.points]
                folium.PolyLine(
                    points,
                    color=color,
                    weight=5,
                    opacity=0.7,
                    popup=f"Segment {segment.segment_id}:<br>"
                    f"Length: {segment.length:.2f} km<br>"
                    f"Elevation Gain: {segment.elevation_gain:.1f}m<br>"
                    f"Avg Slope: {segment.avg_slope:.1f}%",
                ).add_to(map)

        # add difficulty ratings legend
        if include_difficulty:
            cardio = self.analyzer.calculate_cardio_intensity(self)
            technical = self.analyzer.calculate_technical_difficulty(self)
            accessibility = self.analyzer.calculate_accessibility(self)
            weather = self.analyzer.calculate_weather_vulnerability(self)
            overall = self.analyzer.calculate_overall_difficulty(self)

            legend_html = f"""
                <div style="position: fixed; bottom: 50px; right: 50px; width: 200px; 
                height: 180px; border:2px solid grey; z-index:9999; background-color:white;
                padding: 10px; font-size: 14px;">
                <b>Difficulty Ratings</b><br>
                Cardio Intensity: {cardio}/10<br>
                Technical Difficulty: {technical}/10<br>
                Accessibility: {accessibility}/10<br>
                Weather Vulnerability: {weather}/10<br>
                <b>Overall: {overall}/10</b>
                </div>
            """
            map.get_root().html.add_child(folium.Element(legend_html))

        # save the map
        map.save(f"{self.name}_analyzed.html")
        return f"{self.name}_analyzed.html"

    def haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate the distance between two points on Earth"""
        # earth radius in meters
        R = 6371000

        # convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # calcualte differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # haversine formula
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance

    def extract_points(self) -> list[Point]:
        """Extract all points from .geojson file"""
        points = []
        distance_so_far = 0.0

        # ensure we have the full path
        if not os.path.isabs(self.file):
            from utils import get_trail_files

            full_path = os.path.join(get_trail_files(), self.file)
        else:
            full_path = self.file

        # Try to extract points directly from GeoJSON
        try:
            with open(full_path, "r") as f:
                data = json.load(f)

            prev_lat, prev_lon = None, None

            # Process each feature
            for feature in data.get("features", []):
                geometry = feature.get("geometry", {})
                geo_type = geometry.get("type", "")

                # Process MultiLineString type
                if geo_type == "MultiLineString":
                    for line in geometry.get("coordinates", []):
                        for coords in line:
                            if len(coords) >= 3:
                                # GeoJSON standard: [longitude, latitude, elevation]
                                lon, lat, ele = coords[:3]

                                # Calculate distance from previous point
                                if prev_lat is not None and prev_lon is not None:
                                    dist = self.haversine_distance(
                                        prev_lat, prev_lon, lat, lon
                                    )
                                    distance_so_far += dist

                                # Create and store point
                                points.append(
                                    Point(
                                        latitude=lat,
                                        longitude=lon,
                                        elevation=ele,
                                        distance_from_start=distance_so_far,
                                    )
                                )

                                # Update previous coordinates
                                prev_lat, prev_lon = lat, lon

                # Process LineString type
                elif geo_type == "LineString":
                    for coords in geometry.get("coordinates", []):
                        if len(coords) >= 3:
                            lon, lat, ele = coords[:3]

                            if prev_lat is not None and prev_lon is not None:
                                dist = self.haversine_distance(
                                    prev_lat, prev_lon, lat, lon
                                )
                                distance_so_far += dist

                            points.append(
                                Point(
                                    latitude=lat,
                                    longitude=lon,
                                    elevation=ele,
                                    distance_from_start=distance_so_far,
                                )
                            )

                            prev_lat, prev_lon = lat, lon

        except Exception as e:
            print(f"Error extracting points directly from GeoJSON: {e}")

            # Fall back to the original extraction method if direct parsing fails
            try:
                for _, feature in self.gdf.iterrows():
                    geom = feature.geometry

                    # handle LineString
                    if geom.geom_type == "LineString":
                        coords = list(geom.coords)

                        # extract elevation from properties if available
                        elevations = []
                        if "ele" in feature or "elevation" in feature:
                            ele_key = "ele" if "ele" in feature else "elevation"
                            elevations = feature[ele_key]

                            # handle different elevation data formats
                            if isinstance(elevations, (int, float)):
                                elevations = [elevations] * len(coords)
                            elif isinstance(elevations, str):
                                try:
                                    elevations = float(elevations)
                                    elevations = [elevations] * len(coords)
                                except:
                                    elevations = []

                        # fill missing elevations (would use DEM in real implementation)
                        if not elevations or len(elevations) != len(coords):
                            elevations = [0] * len(coords)

                        # create Point objects
                        prev_lat, prev_lon = None, None
                        for i, (lon, lat) in enumerate(coords):
                            if prev_lat is not None and prev_lon is not None:
                                distance_so_far += self.haversine_distance(
                                    prev_lat, prev_lon, lat, lon
                                )

                            points.append(
                                Point(
                                    latitude=lat,
                                    longitude=lon,
                                    elevation=(
                                        elevations[i] if i < len(elevations) else 0
                                    ),
                                    distance_from_start=distance_so_far,
                                )
                            )

                            prev_lat, prev_lon = lat, lon

                    # handle MultiLineString
                    elif geom.geom_type == "MultiLineString":
                        for line in geom.geoms:
                            coords = list(line.coords)

                            # For now, assume constant elevation for MultiLineString
                            # In real implementation, would use elevation service
                            prev_lat, prev_lon = None, None
                            for lon, lat in coords:
                                if prev_lat is not None and prev_lon is not None:
                                    distance_so_far += self.haversine_distance(
                                        prev_lat, prev_lon, lat, lon
                                    )

                                points.append(
                                    Point(
                                        latitude=lat,
                                        longitude=lon,
                                        elevation=0,  # Would use DEM in real implementation
                                        distance_from_start=distance_so_far,
                                    )
                                )

                                prev_lat, prev_lon = lat, lon
            except Exception as inner_e:
                print(f"Fallback extraction also failed: {inner_e}")

        return points

    def calculate_trail_length(self) -> float:
        """Calculates the total length of the trail in km"""
        if not self.points:
            return 0.0

        # use the distance stored in the last point
        return self.points[-1].distance_from_start / 1000.0  # convert to km

    def calculate_elevation_up_down(self) -> Tuple[float, float]:
        """Returns the total increase and decrease in elevation"""
        increase = 0.0
        decrease = 0.0

        if len(self.points) <= 1:
            return increase, decrease

        for i in range(1, len(self.points)):
            elev_diff = self.points[i].elevation - self.points[i - 1].elevation
            if elev_diff > 0:
                increase += elev_diff
            else:
                decrease += elev_diff

        return increase, abs(decrease)

    def calculate_elevation_variance(trail):
        """
        Returns the standard deviation instead of variance for high values
        """
        if len(trail.points) <= 1:
            return 0.0

        elevations = [p.elevation for p in trail.points]

        # Calculate variance
        variance = statistics.variance(elevations) if len(elevations) > 1 else 0.0

        # If variance is above threshold, return standard deviation instead
        if variance > 80:
            return statistics.stdev(elevations)
        else:
            return variance

    def calculate_max_elevation(self) -> float:
        """Get the maximum elevation point"""
        if not self.points:
            return 0.0

        return max(p.elevation for p in self.points)

    def calculate_min_elevation(self) -> float:
        """Get the minimum elevation point"""
        if not self.points:
            return 0.0

        return min(p.elevation for p in self.points)

    def calculate_avg_slope(self) -> float:
        """Calculate the average slope percentage of the entire trail"""
        if self.length == 0 or len(self.points) <= 1:
            return 0.0

        # use total elevation gain for average uphill slope
        return (self.elevation_gain / (self.length * 1000)) * 100

    def calculate_max_slope(self) -> float:
        """Calculate the maximum slope percentage between any two points"""
        if len(self.points) <= 1:
            return 0.0

        max_slope = 0.0
        min_horizontal_distance = 5.0
        for i in range(1, len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]

            # calculate horizontal distance between points
            distance = p2.distance_from_start - p1.distance_from_start

            if distance < min_horizontal_distance or distance == 0:
                continue

            # calculate slope as rise/run * 100
            slope_pct = abs((p2.elevation - p1.elevation) / distance) * 100
            max_slope = max(max_slope, slope_pct)

        return max_slope

    def create_segments(self) -> List[TrailSegment]:
        """Divide the trail into segments for analysis"""
        if not self.points or len(self.points) < 2:
            return []

        segments = []
        segment_points = []
        segment_id = 0
        segment_start_distance = 0

        for i, point in enumerate(self.points):
            segment_points.append(point)

            # check if we've reached the target segment length or if we're at the end of the trail
            current_segment_length = (
                point.distance_from_start - segment_start_distance
            ) / 1000.0
            is_last_point = i == len(self.points) - 1

            if current_segment_length >= self.segment_length or is_last_point:
                if len(segment_points) >= 2:
                    segments.append(TrailSegment(segment_points, segment_id))
                    segment_id += 1

                # start a new segment, but keep the last point as the first point of the new segment
                segment_start_distance = point.distance_from_start
                segment_points = [point]

        return segments

    def analyze_trail(self) -> Dict[str, Any]:
        """
        Perform comprehensive trail analysis
        """
        # calculate all metrics (already done in init)

        # calculate difficulty ratings
        cardio_intensity = self.analyzer.calculate_cardio_intensity(self)
        technical_difficulty = self.analyzer.calculate_technical_difficulty(self)
        accessibility = self.analyzer.calculate_accessibility(self)
        weather_vulnerability = self.analyzer.calculate_weather_vulnerability(self)
        overall_difficulty = self.analyzer.calculate_overall_difficulty(self)

        # return analysis results
        return {
            "trail_name": self.name,
            "length": self.length,
            "elevation_gain": self.elevation_gain,
            "elevation_loss": self.elevation_loss,
            "elevation_range": (self.min_elevation, self.max_elevation),
            "avg_slope": self.avg_slope,
            "max_slope": self.max_slope,
            "segment_count": len(self.segments),
            "difficulty_ratings": {
                "cardio_intensity": cardio_intensity,
                "technical_difficulty": technical_difficulty,
                "accessibility": accessibility,
                "weather_vulnerability": weather_vulnerability,
                "overall_difficulty": overall_difficulty,
            },
        }

    def save_to_database(self, db_connection: sqlite3.Connection) -> bool:
        """Save trail and analysis to database"""
        if not db_connection:
            print("Database connection not provided")
            return False

        # set analyzer's database connectioln
        self.analyzer.db = db_connection

        # store results
        return self.analyzer.store_analysis_results(self)
