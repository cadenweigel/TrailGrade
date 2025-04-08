from dataclasses import dataclass


@dataclass
class Point:
    """Simple Point class to help with Trail"""

    latitude: float
    longitude: float
    elevation: float
    distance_from_start: float = 0.0  # distance from the starting point in meters
