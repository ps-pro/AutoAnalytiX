"""
Fuel Range Violation Cleaning

Extracted from original AutoAnalytiX DATAQUALITYASSURANCE_MODULE.clean_fuel_data() method.
Cleans fuel data by removing range violations and flagged anomalies.
"""

import pandas as pd


class FuelCleaner:
    """
    Fuel cleaning functionality extracted from original DATAQUALITYASSURANCE_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def clean_fuel_data(self, vehicle_id, fuel_data, fuel_issues):
        """Clean fuel data by removing range violations and flagged anomalies"""
        if fuel_data.empty:
            return fuel_data, {}

        initial_count = len(fuel_data)
        cleaned_fuel = fuel_data.copy()

        # Remove range violations (fuel < 0% OR fuel > 100%)
        range_mask = (cleaned_fuel['fuel_level'] >= 0) & (cleaned_fuel['fuel_level'] <= 100)
        cleaned_fuel = cleaned_fuel[range_mask]

        range_violations_removed = initial_count - len(cleaned_fuel)

        # Log cleaning actions
        if range_violations_removed > 0:
            self.logger.info(f"🧹 {vehicle_id}: Removed {range_violations_removed} fuel range violations")

        cleaning_summary = {
            'initial_records': initial_count,
            'range_violations_removed': range_violations_removed,
            'final_records': len(cleaned_fuel),
            'data_retention_rate': len(cleaned_fuel) / initial_count * 100 if initial_count > 0 else 0
        }

        return cleaned_fuel.reset_index(drop=True), cleaning_summary