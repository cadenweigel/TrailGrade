import sqlite3
import statistics
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.trail import Trail


class TrailAnalyzer:
    """Analyzes trail data and generates difficulty ratings"""

    def __init__(self, db_connection: Optional[sqlite3.Connection] = None):
        self.db = db_connection

    def calculate_cardio_intensity(self, trail: "Trail") -> int:
        """
        Calculate cardio intensity 1-10
        Factors: elevation gain, trail length, average slope
        """
        # normalize each factor to a 0-1 scale and then combine

        # elev. gain: 0m (0) to 1500m+ (1.0)
        elevation_factor = min(1.0, trail.elevation_gain / 1500)

        # length: 0km (0) to 20km+ (1.0)
        length_factor = min(1.0, trail.length / 20)

        # avg. slope: 0% (0) to 15%+ (1.0) - adjusted from 30%
        avg_slope = trail.avg_slope if hasattr(trail, "avg_slope") else 0
        slope_factor = min(1.0, avg_slope / 15)

        # add weight to elevation variance for more differentiation
        elev_var = (
            trail.elevation_variance if hasattr(trail, "elevation_variance") else 0
        )
        var_factor = min(1.0, elev_var / 100)

        # combined score with weights
        combined_score = (
            elevation_factor * 0.4
            + length_factor * 0.3
            + slope_factor * 0.2
            + var_factor * 0.1
        )

        # convert to 1-10 scale and round
        return max(1, min(10, round(combined_score * 9) + 1))

    def calculate_technical_difficulty(self, trail: "Trail") -> int:
        """
        Calculate technical difficulty 1-10
        Factors: max slope, terrain type, obstacles, exposure
        """
        # use only max slope and elevation variance in lieu of technical terrain data

        # max slope: 0% (0) to 67%+ (1.0)
        max_slope = trail.max_slope if hasattr(trail, "max_slope") else 0
        slope_factor = min(1.0, max_slope / 67)

        # elevation variance (proxy for technical terrain)
        elev_variance = (
            trail.elevation_variance if hasattr(trail, "elevation_variance") else 0
        )
        variance_factor = min(1.0, elev_variance / 200)

        # combined score
        combined_score = slope_factor * 0.6 + variance_factor * 0.4

        # convert to 1-10 scale and round
        return max(1, min(10, round(combined_score * 9) + 1))

    def calculate_accessibility(self, trail: "Trail") -> int:
        """
        Calculate accessibility score (higher = more accessible) 1-10
        Factors: technical difficulty (inverse), rest tbd
        """
        # placeholder
        pass

    def calculate_weather_vulnerability(self, trail: "Trail") -> int:
        """
        Calculate weather vulnerability 1-10
        Factors: elevation, exposure, tree cover (estimated)
        """
        # placeholder, need additional data sources for tree cover and exposure
        pass

    def calculate_elevation_variance(trail: "Trail"):
        """
        Enhanced method to calculate elevation variance with better sensitivity
        """
        if len(trail.points) <= 1:
            return 0.0

        # Get all elevations
        elevations = [p.elevation for p in trail.points]

        # Calculate several variance metrics for better differentiation
        if len(elevations) > 1:
            # Standard variance
            var = statistics.variance(elevations) if len(elevations) > 1 else 0.0

            # Range (max - min)
            elev_range = max(elevations) - min(elevations)

            # Standard deviation
            std_dev = statistics.stdev(elevations) if len(elevations) > 1 else 0.0

            # Calculate elevation changes (ups and downs)
            elev_changes = sum(
                abs(elevations[i] - elevations[i - 1])
                for i in range(1, len(elevations))
            )
            avg_change = elev_changes / len(elevations)

            # Combined metric (weighted blend)
            combined_variance = (
                var * 0.3 + elev_range * 0.3 + std_dev * 0.2 + avg_change * 0.2
            )

            return combined_variance

        return 0.0

    def calculate_overall_difficulty(self, trail: "Trail") -> int:
        """Calculate overall difficulty score"""
        cardio = self.calculate_cardio_intensity(trail)
        technical = self.calculate_technical_difficulty(trail)
        accessibility = self.calculate_accessibility(trail)
        weather = self.calculate_weather_vulnerability(trail)

        # inverse of accessibility (lower accessibility = higher diff)
        # accessibility_inverted = 11 - accessibility

        # weighted combination
        overall = (
            cardio * 0.6
            + technical * 0.4
            # accessibility_inverted * 0.2 +
            # weather * 0.1
        )

        return max(1, min(10, round(overall)))

    def store_analysis_results(self, trail: "Trail") -> bool:
        """Store trail analysis in the database"""
        if not self.db:
            print("Database connection not provided.")
            return False

        try:
            cursor = self.db.cursor()

            # get the trail locatioln
            location_lat, location_long = trail.get_location_coordinates()

            # extract filename only for storage for portability
            from utils import get_trail_file_name

            file_name = get_trail_file_name(trail.file)

            # first, store the trail data
            cursor.execute(
                """
                INSERT INTO trails (
                    name, location_lat, location_long, length, elevation_gain, 
                    elevation_loss, max_elevation, min_elevation,
                    geojson_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    trail.name,
                    location_lat,
                    location_long,
                    trail.length,
                    trail.elevation_gain,
                    trail.elevation_loss,
                    trail.max_elevation,
                    trail.min_elevation,
                    file_name,
                ),
            )

            trail_id = cursor.lastrowid

            # store segments
            for segment in trail.segments:
                segment_data = segment.to_dict()
                cursor.execute(
                    """
                    INSERT INTO trail_segments (
                        trail_id, segment_order, start_lat, start_long,
                        end_lat, end_long, length, elevation_gain,
                        elevation_loss, avg_slope, max_slope, terrain_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        trail_id,
                        segment_data["segment_id"],
                        segment_data["start_lat"],
                        segment_data["start_long"],
                        segment_data["end_lat"],
                        segment_data["end_long"],
                        segment_data["length"],
                        segment_data["elevation_gain"],
                        segment_data["elevation_loss"],
                        segment_data["avg_slope"],
                        segment_data["max_slope"],
                        segment_data["terrain_type"],
                    ),
                )

            # store difficulty ratings
            cursor.execute(
                """
                INSERT INTO difficulty_ratings (
                    trail_id, cardio_intensity, technical_difficulty,
                    accessibility, weather_vulnerability, overall_difficulty
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    trail_id,
                    self.calculate_cardio_intensity(trail),
                    self.calculate_technical_difficulty(trail),
                    self.calculate_accessibility(trail),
                    self.calculate_weather_vulnerability(trail),
                    self.calculate_overall_difficulty(trail),
                ),
            )

            self.db.commit()
            return True

        except Exception as e:
            print(f"Error storing trail analysis: {e}")
            if self.db:
                self.db.rollback()
            return False


def connect_to_database(db_path) -> None:
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect(db_path)

        conn.commit()
        return conn

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
