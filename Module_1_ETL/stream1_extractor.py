"""
Wide-format Telemetry Processing

Extracted from original AutoAnalytiX ETL_MODULE.extract_meter_data_from_stream1() method.
Processes wide-format telemetry data preserving sensor characteristics.
"""

import pandas as pd
from collections import defaultdict
from tqdm import tqdm


class Stream1Extractor:
    """
    Stream1 extraction functionality extracted from original ETL_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def extract_meter_data_from_stream1(self, telemetry_1):
        """Extract individual meter data from wide-format telemetry stream"""
        self.logger.info("🔄 Processing Telemetry Stream 1 (Wide Format)")

        vehicle_meter_data = defaultdict(lambda: defaultdict(pd.DataFrame))
        unique_vehicles = telemetry_1['vehicle_id'].unique()

        # Process each vehicle individually to preserve sensor characteristics
        for vehicle_id in tqdm(unique_vehicles, desc="Processing vehicles (Stream 1)"):
            vehicle_data = telemetry_1[telemetry_1['vehicle_id'] == vehicle_id].copy()
            vehicle_data = vehicle_data.sort_values('TIMESTAMP')

            # Extract Speed Data - preserve all speed readings with timestamps
            speed_mask = vehicle_data['speed'].notna()
            if speed_mask.any():
                speed_data = vehicle_data.loc[speed_mask, ['TIMESTAMP', 'speed']].reset_index(drop=True)
                vehicle_meter_data[vehicle_id]['speed'] = speed_data

            # Extract Odometer Data - critical for distance calculations
            odometer_mask = vehicle_data['odometer'].notna()
            if odometer_mask.any():
                odometer_data = vehicle_data.loc[odometer_mask, ['TIMESTAMP', 'odometer']].reset_index(drop=True)
                vehicle_meter_data[vehicle_id]['odometer'] = odometer_data

            # Extract Fuel Level Data - essential for theft detection
            fuel_mask = vehicle_data['fuel_level'].notna()
            if fuel_mask.any():
                fuel_data = vehicle_data.loc[fuel_mask, ['TIMESTAMP', 'fuel_level']].reset_index(drop=True)
                vehicle_meter_data[vehicle_id]['fuel'] = fuel_data

        self.logger.info(f"[OK] Stream 1 processed: {len(unique_vehicles)} vehicles")
        return dict(vehicle_meter_data)