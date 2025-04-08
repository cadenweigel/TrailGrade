#!/usr/bin/env python
"""
Enhanced Validation Script for Trail Difficulty Ratings.
This script:
1. Analyzes multiple trails
2. Provides detailed metrics for each trail
3. Generates summary statistics
4. Creates visualizations

Usage:
    python test_trail_difficulty.py

Make sure to run this from the tests/ directory.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Import the TrailAnalyzer from core
from core.trail import Trail, TrailAnalyzer


def analyze_multiple_trails(trail_files_dir, max_trails=None):
    """
    Analyze multiple trails and collect their metrics.

    Args:
        trail_files_dir (str): Directory containing trail files
        max_trails (int, optional): Maximum number of trails to analyze

    Returns:
        list: List of dictionaries containing trail metrics
    """
    print(f"\n=== Analyzing trails from {trail_files_dir} ===")

    # Get list of trail files
    trail_files = [
        os.path.join(trail_files_dir, f)
        for f in os.listdir(trail_files_dir)
        if f.endswith(".geojson")
    ]

    if not trail_files:
        print(f"No .geojson files found in {trail_files_dir}")
        return None

    # Limit the number of trails to analyze if specified
    if max_trails:
        trail_files = trail_files[:max_trails]
    print(f"Analyzing {len(trail_files)} trails...")

    # Create analyzer
    analyzer = TrailAnalyzer()

    # Results list
    results = []

    # Process each trail
    for i, trail_file in enumerate(trail_files, 1):
        try:
            print(
                f"\nProcessing trail {i}/{len(trail_files)}: {os.path.basename(trail_file)}"
            )

            # Load and analyze trail
            trail = Trail(trail_file, analyzer=analyzer)

            # Calculate metrics
            cardio = analyzer.calculate_cardio_intensity(trail)
            technical = analyzer.calculate_technical_difficulty(trail)
            overall = analyzer.calculate_overall_difficulty(trail)

            # Create detailed trail result
            trail_result = {
                "name": trail.name,
                "length": round(trail.length, 2),
                "elevation_gain": round(trail.elevation_gain, 2),
                "elevation_loss": round(trail.elevation_loss, 2),
                "max_elevation": round(trail.max_elevation, 2),
                "min_elevation": round(trail.min_elevation, 2),
                "avg_slope": round(trail.avg_slope, 2),
                "max_slope": round(trail.max_slope, 2),
                "elevation_variance": round(trail.elevation_variance, 2),
                "cardio_intensity": cardio,
                "technical_difficulty": technical,
                "overall_difficulty": overall,
            }

            # Print individual trail details
            print("\nTrail Details:")
            for key, value in trail_result.items():
                print(f"{key.replace('_', ' ').title()}: {value}")

            results.append(trail_result)

        except Exception as e:
            print(f"Error processing trail {trail_file}: {e}")

    print(f"\nSuccessfully analyzed {len(results)} trails")
    return results


def analyze_trail_metrics(results):
    """
    Perform comprehensive analysis of trail metrics.

    Args:
        results (list): List of trail metrics

    Returns:
        pandas.DataFrame: DataFrame containing trail metrics
    """
    if not results:
        print("No results to analyze")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Detailed statistical summary
    print("\n=== Trail Metrics Summary ===")

    # Print total number of trails
    print(f"\nTotal Trails Analyzed: {len(df)}")

    # Descriptive statistics columns
    stats_columns = [
        "length",
        "elevation_gain",
        "avg_slope",
        "max_slope",
        "elevation_variance",
        "cardio_intensity",
        "technical_difficulty",
        "overall_difficulty",
    ]

    # Descriptive statistics summary
    print("\nDescriptive Statistics:")
    stats = df[stats_columns].describe()

    # Transpose and round for better readability
    stats_transposed = stats.T.round(2)

    # Custom print of statistics (excluding count)
    stats_to_print = ["mean", "std", "min", "25%", "50%", "75%", "max"]
    for col in stats_columns:
        print(f"\n{col.replace('_', ' ').title()}:")
        col_stats = stats_transposed.loc[col]
        for stat in stats_to_print:
            value = col_stats[stat]
            print(f"  {stat.replace('_', ' ').title()}: {value}")

    # Difficulty distribution
    print("\n=== Difficulty Distribution ===")
    difficulty_dist = df["overall_difficulty"].value_counts().sort_index()
    print("\nOverall Difficulty Distribution:")
    for diff_level, count in difficulty_dist.items():
        print(f"  Level {diff_level}: {count} trails ({count/len(df)*100:.1f}%)")

    return df


def main():
    """Run the validation process."""
    # Set the directory containing trail files
    trail_files_dir = os.path.join(project_root, "storage", "trail_files")

    # Analyze multiple trails
    results = analyze_multiple_trails(trail_files_dir)

    if results:
        # Analyze and visualize trail metrics
        analyze_trail_metrics(results)

        print("\nTrail difficulty analysis complete!")


if __name__ == "__main__":
    main()
