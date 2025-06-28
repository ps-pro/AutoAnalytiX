"""
Fuel Pattern Analysis and Range Validation

Extracted from original AutoAnalytiX DATAQUALITYINSPECTION_MODULE.analyze_fuel_patterns() method.
Advanced fuel pattern analysis with range violation detection.
"""

import pandas as pd
import numpy as np


class FuelAnalyzer:
    """
    Fuel analysis functionality extracted from original DATAQUALITYINSPECTION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def calculate_moving_averages(self, data_series, windows=[5, 10]):
        """Calculate multiple moving averages for fuel trend analysis"""
        moving_averages = {}

        for window in windows:
            if len(data_series) >= window:
                ma = data_series.rolling(window=window, center=True).mean()
                moving_averages[f'MA_{window}'] = ma
            else:
                # If insufficient data, create MA with available data
                moving_averages[f'MA_{window}'] = data_series.rolling(window=len(data_series), center=True).mean()

        return moving_averages

    def analyze_fuel_patterns(self, vehicle_id, fuel_data):
        """Advanced fuel pattern analysis with range violation detection"""
        if len(fuel_data) < 2:
            self.logger.warning(f"⚠️  {vehicle_id}: Insufficient fuel data for analysis")
            return None

        # Sort data for chronological analysis
        fuel_sorted = fuel_data.sort_values('TIMESTAMP').copy()
        fuel_levels = fuel_sorted['fuel_level']
        timestamps = fuel_sorted['TIMESTAMP']

        # Calculate moving averages for fuel trend analysis
        moving_averages = self.calculate_moving_averages(fuel_levels, windows=[5, 10])

        # Identify range violations (physically impossible readings)
        range_violations = (fuel_levels < 0) | (fuel_levels > 100)
        range_violation_data = fuel_sorted[range_violations].copy()

        # Identify large fuel drops for further investigation
        fuel_changes = fuel_levels.diff()
        large_drops = fuel_changes < -20  # More than 20% drop
        large_drop_data = fuel_sorted[large_drops].copy()

        # Calculate comprehensive fuel statistics
        fuel_stats = {
            'total_readings': len(fuel_data),
            'min_fuel': fuel_levels.min(),
            'max_fuel': fuel_levels.max(),
            'mean_fuel': fuel_levels.mean(),
            'std_fuel': fuel_levels.std(),
            'range_violations': range_violations.sum(),
            'large_drops': large_drops.sum(),
            'negative_readings': (fuel_levels < 0).sum(),
            'over_100_readings': (fuel_levels > 100).sum(),
            'time_span_days': (timestamps.max() - timestamps.min()).days
        }

        # Data quality assessment based on range violations
        violation_rate = range_violations.sum() / len(fuel_levels) * 100
        data_quality_score = max(0, 100 - violation_rate * 10)

        # Log critical fuel anomalies
        if fuel_stats['range_violations'] > 0:
            self.logger.log_vehicle_violation(vehicle_id, "FUEL_RANGE_VIOLATION", {
                "Violation Type": "Fuel Range Violations (CRITICAL)",
                "Total Range Violations": fuel_stats['range_violations'],
                "Negative Readings": fuel_stats['negative_readings'],
                "Over 100% Readings": fuel_stats['over_100_readings'],
                "Large Drops (>20%)": fuel_stats['large_drops'],
                "Data Quality Score": f"{data_quality_score:.1f}%",
                "Risk Level": "CRITICAL"
            })

        return {
            'vehicle_id': vehicle_id,
            'statistics': fuel_stats,
            'moving_averages': moving_averages,
            'range_violations': range_violation_data,
            'large_drops': large_drop_data,
            'data_quality_score': data_quality_score,
            'raw_data': fuel_sorted
        }