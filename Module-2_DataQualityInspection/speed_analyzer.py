"""
Speed Pattern Analysis and Acceleration

Extracted from original AutoAnalytiX DATAQUALITYINSPECTION_MODULE.analyze_speed_patterns() method.
Advanced speed pattern analysis with acceleration distribution.
"""

import pandas as pd
import numpy as np


class SpeedAnalyzer:
    """
    Speed analysis functionality extracted from original DATAQUALITYINSPECTION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def analyze_speed_patterns(self, vehicle_id, speed_data):
        """Advanced speed pattern analysis with acceleration distribution"""
        if len(speed_data) < 2:
            self.logger.warning(f"⚠️  {vehicle_id}: Insufficient speed data for analysis")
            return None

        # Sort data and calculate time-based metrics
        speed_sorted = speed_data.sort_values('TIMESTAMP').copy()
        speed_values = speed_sorted['speed']
        timestamps = speed_sorted['TIMESTAMP']

        # Calculate acceleration patterns (mph/min)
        time_diffs = timestamps.diff().dt.total_seconds() / 60  # Convert to minutes
        speed_changes = speed_values.diff().abs()

        # Filter valid acceleration calculations (reasonable time gaps)
        valid_mask = (time_diffs > 0) & (time_diffs < 60)  # Between 0 and 60 minutes
        valid_accelerations = (speed_changes / time_diffs)[valid_mask]

        if len(valid_accelerations) == 0:
            self.logger.warning(f"⚠️  {vehicle_id}: No valid acceleration data points")
            return None

        # Calculate comprehensive acceleration statistics
        acceleration_stats = {
            'total_readings': len(speed_data),
            'valid_accelerations': len(valid_accelerations),
            'mean_acceleration': valid_accelerations.mean(),
            'std_acceleration': valid_accelerations.std(),
            'max_acceleration': valid_accelerations.max(),
            'percentile_95': valid_accelerations.quantile(0.95),
            'percentile_99': valid_accelerations.quantile(0.99),
            'median_acceleration': valid_accelerations.median()
        }

        # Threshold impact analysis for specific acceleration thresholds
        acceleration_thresholds = [10, 20, 30, 40, 50, 75, 100]
        threshold_analysis = {}

        for threshold in acceleration_thresholds:
            violations = (valid_accelerations > threshold).sum()
            threshold_analysis[threshold] = {
                'violations': violations,
                'percentage': violations / len(valid_accelerations) * 100 if len(valid_accelerations) > 0 else 0
            }

        # Data quality assessment
        data_quality_score = min(100, (len(valid_accelerations) / len(speed_data)) * 100)

        # Identify severe acceleration violations for logging
        severe_violations = (valid_accelerations > 50).sum()
        if severe_violations > 0:
            self.logger.log_vehicle_violation(vehicle_id, "HIGH_ACCELERATION", {
                "Violation Type": "Excessive Acceleration Events",
                "Severe Violations (>50 mph/min)": severe_violations,
                "Max Acceleration": f"{acceleration_stats['max_acceleration']:.2f} mph/min",
                "95th Percentile": f"{acceleration_stats['percentile_95']:.2f} mph/min",
                "Data Quality Score": f"{data_quality_score:.1f}%",
                "Risk Level": "HIGH" if severe_violations > 10 else "MEDIUM"
            })

        return {
            'vehicle_id': vehicle_id,
            'statistics': acceleration_stats,
            'threshold_analysis': threshold_analysis,
            'data_quality_score': data_quality_score,
            'valid_accelerations': valid_accelerations,
            'raw_data': speed_sorted
        }