"""
Odometer Analysis and Reset Detection

Extracted from original AutoAnalytiX DATAQUALITYINSPECTION_MODULE.analyze_odometer_patterns() method.
Advanced odometer pattern analysis with moving average reset detection.
"""

import pandas as pd
import numpy as np


class OdometerAnalyzer:
    """
    Odometer analysis functionality extracted from original DATAQUALITYINSPECTION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def calculate_moving_averages(self, data_series, windows=[5, 10, 20]):
        """Calculate multiple moving averages for gradient analysis"""
        moving_averages = {}

        for window in windows:
            if len(data_series) >= window:
                ma = data_series.rolling(window=window, center=True).mean()
                moving_averages[f'MA_{window}'] = ma
            else:
                # If insufficient data, create MA with available data
                moving_averages[f'MA_{window}'] = data_series.rolling(window=len(data_series), center=True).mean()

        return moving_averages

    def analyze_odometer_patterns(self, vehicle_id, odometer_data):
        """Advanced odometer pattern analysis with moving average reset detection"""
        if len(odometer_data) < 2:
            self.logger.warning(f"⚠️  {vehicle_id}: Insufficient odometer data for analysis")
            return None

        # Sort data for chronological analysis
        odometer_sorted = odometer_data.sort_values('TIMESTAMP').copy()
        odometer_values = odometer_sorted['odometer']
        timestamps = odometer_sorted['TIMESTAMP']

        # Calculate multiple moving averages for gradient analysis
        moving_averages = self.calculate_moving_averages(odometer_values, windows=[5, 10, 20])

        # Identify zero readings and their contexts
        zero_readings = odometer_sorted[odometer_values == 0].copy()
        odometer_changes = odometer_values.diff()
        decreases = odometer_changes < 0
        large_decreases = odometer_changes < -50

        # Advanced reset classification using moving average analysis
        reset_classifications = []

        for idx, reading in zero_readings.iterrows():
            timestamp = reading['TIMESTAMP']

            # Find position in the sorted data for context analysis
            position = odometer_sorted[odometer_sorted['TIMESTAMP'] == timestamp].index[0]

            # Analyze moving average behavior around zero reading
            context_window = slice(max(0, position-10), min(len(odometer_sorted), position+10))
            context_ma_5 = moving_averages['MA_5'].iloc[context_window]
            context_ma_10 = moving_averages['MA_10'].iloc[context_window]
            context_ma_20 = moving_averages['MA_20'].iloc[context_window]

            # Classification logic based on moving average patterns
            if len(context_ma_5.dropna()) > 5:
                ma_all_low = (context_ma_5 < 1000).sum() > 5  # Threshold for "low" readings
                ma_recovery = context_ma_5.iloc[-3:].mean() > context_ma_5.iloc[:3].mean()

                if ma_all_low and not ma_recovery:
                    classification = "LEGITIMATE_RESET"
                else:
                    classification = "FAULTY_SENSOR_READING"
            else:
                classification = "INSUFFICIENT_CONTEXT"

            reset_classifications.append({
                'timestamp': timestamp,
                'position': position,
                'classification': classification,
                'context_quality': len(context_ma_5.dropna())
            })

        # Calculate comprehensive odometer statistics
        odometer_stats = {
            'total_readings': len(odometer_data),
            'min_odometer': odometer_values.min(),
            'max_odometer': odometer_values.max(),
            'total_distance': odometer_values.max() - odometer_values.min(),
            'zero_readings': len(zero_readings),
            'decreases': decreases.sum(),
            'large_decreases': large_decreases.sum(),
            'legitimate_resets': len([r for r in reset_classifications if r['classification'] == 'LEGITIMATE_RESET']),
            'faulty_sensor_readings': len([r for r in reset_classifications if r['classification'] == 'FAULTY_SENSOR_READING']),
            'time_span_days': (timestamps.max() - timestamps.min()).days
        }

        # Data quality assessment
        decrease_rate = decreases.sum() / len(odometer_values) * 100
        data_quality_score = max(0, 100 - decrease_rate * 2)

        # Log significant odometer anomalies
        total_anomalies = odometer_stats['zero_readings'] + odometer_stats['decreases']
        if total_anomalies > 0:
            self.logger.log_vehicle_violation(vehicle_id, "ODOMETER_ANOMALY", {
                "Violation Type": "Odometer Reading Anomalies",
                "Zero Readings": odometer_stats['zero_readings'],
                "Odometer Decreases": odometer_stats['decreases'],
                "Large Decreases (>50mi)": odometer_stats['large_decreases'],
                "Legitimate Resets": odometer_stats['legitimate_resets'],
                "Faulty Sensor Readings": odometer_stats['faulty_sensor_readings'],
                "Data Quality Score": f"{data_quality_score:.1f}%",
                "Risk Level": "HIGH" if total_anomalies > 10 else "MEDIUM"
            })

        return {
            'vehicle_id': vehicle_id,
            'statistics': odometer_stats,
            'moving_averages': moving_averages,
            'zero_readings': zero_readings,
            'reset_classifications': reset_classifications,
            'data_quality_score': data_quality_score,
            'raw_data': odometer_sorted
        }