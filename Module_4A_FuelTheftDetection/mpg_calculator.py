"""
Real-time MPG Calculations

Extracted from original AutoAnalytiX FUEL_THEFT_DETECTION_MODULE.calculate_real_time_mpg() method.
Calculates real-time MPG for each synchronized window pair.
"""

import pandas as pd
import numpy as np


class MPGCalculator:
    """
    MPG calculation functionality extracted from original FUEL_THEFT_DETECTION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def calculate_real_time_mpg(self, vehicle_id, sync_data, tank_capacity):
        """Calculate real-time MPG for each synchronized window pair"""
        if len(sync_data) < 2:
            return sync_data

        mpg_data = sync_data.copy()
        mpg_data['distance_delta'] = mpg_data['odometer'].diff()
        mpg_data['fuel_delta'] = mpg_data['fuel_level'].diff() * -1  # Fuel decreases, so invert
        mpg_data['fuel_gallons_consumed'] = (mpg_data['fuel_delta'] / 100) * tank_capacity
        mpg_data['time_delta_hours'] = mpg_data['timestamp'].diff().dt.total_seconds() / 3600

        # Calculate MPG where fuel was actually consumed
        mpg_data['calculated_mpg'] = np.where(
            mpg_data['fuel_gallons_consumed'] > 0,
            mpg_data['distance_delta'] / mpg_data['fuel_gallons_consumed'],
            np.nan
        )

        # Apply physics-based validation thresholds
        mpg_data['mpg_validation'] = np.where(
            mpg_data['calculated_mpg'].isna(), 'NO_FUEL_CONSUMPTION',
            np.where(mpg_data['calculated_mpg'] > 50, 'FUEL_SENSOR_ERROR',
                    np.where(mpg_data['calculated_mpg'] < 2, 'INVESTIGATE_POTENTIAL_THEFT',
                            'NORMAL_OPERATION'))
        )

        # Log validation results
        validation_summary = mpg_data['mpg_validation'].value_counts().to_dict()
        for status, count in validation_summary.items():
            if status in ['FUEL_SENSOR_ERROR', 'INVESTIGATE_POTENTIAL_THEFT'] and count > 0:
                self.logger.warning(f"⚠️  {vehicle_id}: {count} windows flagged as {status}")

        return mpg_data