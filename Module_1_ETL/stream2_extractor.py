"""
Long-format Parameter-Value Processing

Extracted from original AutoAnalytiX ETL_MODULE.extract_meter_data_from_stream2() method.
Processes long-format parameter-value telemetry stream.
"""

import pandas as pd
from collections import defaultdict
from tqdm import tqdm


class Stream2Extractor:
    """
    Stream2 extraction functionality extracted from original ETL_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def extract_meter_data_from_stream2(self, telemetry_2):
        """Extract meter data from long-format parameter-value telemetry stream"""
        self.logger.info("🔄 Processing Telemetry Stream 2 (Long Format)")

        vehicle_meter_data = defaultdict(lambda: defaultdict(pd.DataFrame))
        unique_vehicles = telemetry_2['vehicle_id'].unique()

        # Define parameter mapping for robust extraction
        parameter_mapping = {
            'speed': 'speed',
            'odometer': 'odometer',
            'fuel_level': 'fuel'
        }

        for vehicle_id in tqdm(unique_vehicles, desc="Processing vehicles (Stream 2)"):
            vehicle_data = telemetry_2[telemetry_2['vehicle_id'] == vehicle_id].copy()

            # Process each meter type separately to maintain data integrity
            for param_name, meter_type in parameter_mapping.items():
                param_data = vehicle_data[vehicle_data['name'] == param_name].copy()

                if len(param_data) > 0:
                    # Convert parameter-value format to structured format
                    meter_df = param_data[['TIMESTAMP', 'val']].copy()
                    meter_df.rename(columns={'val': param_name}, inplace=True)

                    # Apply robust numeric conversion with error handling
                    meter_df[param_name] = pd.to_numeric(meter_df[param_name], errors='coerce')
                    meter_df = meter_df.dropna(subset=[param_name])

                    if len(meter_df) > 0:
                        meter_df = meter_df.sort_values('TIMESTAMP').reset_index(drop=True)
                        vehicle_meter_data[vehicle_id][meter_type] = meter_df

        self.logger.info(f"[OK] Stream 2 processed: {len(unique_vehicles)} vehicles")
        return dict(vehicle_meter_data)