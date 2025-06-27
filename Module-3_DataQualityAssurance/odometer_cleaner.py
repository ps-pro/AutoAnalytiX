"""
Odometer Data Cleaning (Zero Removal, etc.)

Extracted from original AutoAnalytiX DATAQUALITYASSURANCE_MODULE.clean_odometer_data() method.
Cleans odometer data by removing zero readings and faulty sensor readings.
"""

import pandas as pd


class OdometerCleaner:
    """
    Odometer cleaning functionality extracted from original DATAQUALITYASSURANCE_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def clean_odometer_data(self, vehicle_id, odometer_data, odometer_issues):
        """Clean odometer data by removing zero readings and faulty sensor readings"""
        if odometer_data.empty:
            return odometer_data, {}

        initial_count = len(odometer_data)
        cleaned_odometer = odometer_data.copy()

        # Remove all zero readings (as per specification)
        zero_mask = cleaned_odometer['odometer'] != 0
        cleaned_odometer = cleaned_odometer[zero_mask]
        zero_readings_removed = initial_count - len(cleaned_odometer)

        # Remove readings flagged as "FAULTY_SENSOR_READING" from Module 2 analysis
        faulty_readings_removed = 0
        if 'reset_classifications' in odometer_issues:
            faulty_timestamps = [
                r['timestamp'] for r in odometer_issues['reset_classifications']
                if r['classification'] == 'FAULTY_SENSOR_READING'
            ]

            if faulty_timestamps:
                # Remove faulty sensor readings identified by moving average analysis
                faulty_mask = ~cleaned_odometer['TIMESTAMP'].isin(faulty_timestamps)
                initial_after_zero = len(cleaned_odometer)
                cleaned_odometer = cleaned_odometer[faulty_mask]
                faulty_readings_removed = initial_after_zero - len(cleaned_odometer)

        # Log cleaning actions
        total_removed = zero_readings_removed + faulty_readings_removed
        if total_removed > 0:
            self.logger.info(f"🧹 {vehicle_id}: Removed {zero_readings_removed} zero readings, "
                           f"{faulty_readings_removed} faulty sensor readings")

        cleaning_summary = {
            'initial_records': initial_count,
            'zero_readings_removed': zero_readings_removed,
            'faulty_readings_removed': faulty_readings_removed,
            'total_removed': total_removed,
            'final_records': len(cleaned_odometer),
            'data_retention_rate': len(cleaned_odometer) / initial_count * 100 if initial_count > 0 else 0
        }

        return cleaned_odometer.reset_index(drop=True), cleaning_summary