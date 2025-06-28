"""
Speed Data Cleaning Logic

Extracted from original AutoAnalytiX DATAQUALITYASSURANCE_MODULE.clean_speed_data() method.
Cleans speed data (minimal cleaning - mostly validation).
"""

import pandas as pd


class SpeedCleaner:
    """
    Speed cleaning functionality extracted from original DATAQUALITYASSURANCE_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def clean_speed_data(self, vehicle_id, speed_data, speed_issues):
        """Clean speed data (minimal cleaning - mostly validation)"""
        if speed_data.empty:
            return speed_data, {}

        initial_count = len(speed_data)
        cleaned_speed = speed_data.copy()

        # Remove clearly invalid speed readings (negative speeds)
        valid_mask = cleaned_speed['speed'] >= 0
        cleaned_speed = cleaned_speed[valid_mask]

        invalid_removed = initial_count - len(cleaned_speed)

        if invalid_removed > 0:
            self.logger.info(f"🧹 {vehicle_id}: Removed {invalid_removed} invalid speed readings")

        cleaning_summary = {
            'initial_records': initial_count,
            'invalid_readings_removed': invalid_removed,
            'final_records': len(cleaned_speed),
            'data_retention_rate': len(cleaned_speed) / initial_count * 100 if initial_count > 0 else 0
        }

        return cleaned_speed.reset_index(drop=True), cleaning_summary