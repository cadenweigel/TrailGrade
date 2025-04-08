from typing import List, Dict
from .point import Point


class TrailSegment:
    """Represents a segement of a trail with analysis metrics"""

    def __init__(self, points: List[Point], segment_id: int):
        self.segment_id = segment_id
        self.points = points
        self.start_point = points[0]
        self.end_point = points[-1]
        self.length = self._calculate_length()
        self.elevation_gain = self._calculate_elevation_gain()
        self.elevation_loss = self._calculate_elevation_loss()
        self.avg_slope = self._calculate_avg_slope()
        self.max_slope = self._calculate_max_slope()

    def _calculate_length(self) -> float:
        """Calculate the length of a segment in kilometers"""
        if len(self.points) <= 1:
            return 0.0

        # distance is already calculated and stored in the last point
        return self.points[-1].distance_from_start / 1000.0  # m to km

    def _calculate_elevation_gain(self) -> float:
        """Calculate total elevation gain in the segment"""
        if len(self.points) <= 1:
            return 0.0

        gain = 0.0
        for i in range(1, len(self.points)):
            elev_diff = self.points[i].elevation - self.points[i - 1].elevation
            if elev_diff > 0:
                gain += elev_diff
        return gain

    def _calculate_elevation_loss(self) -> float:
        """Calculate total elevation loss in the segment"""
        if len(self.points) <= 1:
            return 0.0

        loss = 0.0
        for i in range(1, len(self.points)):
            elev_diff = self.points[i - 1].elevation - self.points[i].elevation
            if elev_diff > 0:
                loss += elev_diff
        return loss

    def _calculate_avg_slope(self) -> float:
        """Calculate average slope percentage of the segment"""
        if self.length == 0:
            return 0.0

        # convert elevation gain to meters, length to meters
        length_m = self.length * 1000
        avg_slope_pct = (self.elevation_gain / length_m) * 100
        return avg_slope_pct

    def _calculate_max_slope(self) -> float:
        """Calculate maximum slope percentage between any two points"""
        if len(self.points) <= 1:
            return 0.0

        max_slope = 0.0
        for i in range(1, len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]

            # distance between p1 and p2 in meters
            distance = p2.distance_from_start - p1.distance_from_start

            if distance == 0:
                continue

            elev_diff = abs(p2.elevation - p1.elevation)
            slope_pct = (elev_diff / distance) * 100
            max_slope = max(max_slope, slope_pct)

        return max_slope

    def get_terrain_type(self) -> str:
        """Placeholder for terrain type detection"""
        # for now, basic estimation based on slope
        if self.avg_slope > 15:
            return "steep"
        elif self.avg_slope > 8:
            return "moderate"
        else:
            return "flat"

    def to_dict(self) -> Dict:
        """Convert segment data to a dictionary for database storage"""
        return {
            "segment_id": self.segment_id,
            "start_lat": self.start_point.latitude,
            "start_long": self.start_point.longitude,
            "end_lat": self.end_point.latitude,
            "end_long": self.end_point.longitude,
            "length": self.length,
            "elevation_gain": self.elevation_gain,
            "elevation_loss": self.elevation_loss,
            "avg_slope": self.avg_slope,
            "max_slope": self.max_slope,
            "terrain_type": self.get_terrain_type(),
        }
