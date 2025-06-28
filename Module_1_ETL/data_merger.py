"""
Stream Merging and Deduplication

Extracted from original AutoAnalytiX ETL_MODULE.merge_meter_data_streams() method.
Intelligently merges meter data from both telemetry streams with deduplication.
"""

import pandas as pd
from collections import defaultdict
from tqdm import tqdm


class DataMerger:
    """
    Data merging functionality extracted from original ETL_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def merge_meter_data_streams(self, stream1_data, stream2_data):
        """Intelligently merge meter data from both telemetry streams"""
        self.logger.info("🔗 Merging Data Streams with Deduplication")

        merged_vehicle_data = defaultdict(lambda: defaultdict(pd.DataFrame))
        all_vehicles = set(stream1_data.keys()) | set(stream2_data.keys())

        merge_stats = {
            'vehicles_processed': 0,
            'meters_merged': 0,
            'duplicates_removed': 0
        }

        for vehicle_id in tqdm(all_vehicles, desc="Merging vehicle data"):
            merge_stats['vehicles_processed'] += 1

            for meter_type in ['speed', 'odometer', 'fuel']:
                stream1_meter = stream1_data.get(vehicle_id, {}).get(meter_type, pd.DataFrame())
                stream2_meter = stream2_data.get(vehicle_id, {}).get(meter_type, pd.DataFrame())

                # Handle different merge scenarios based on data availability
                if len(stream1_meter) == 0 and len(stream2_meter) == 0:
                    continue  # No data from either stream
                elif len(stream1_meter) == 0:
                    merged_data = stream2_meter.copy()
                elif len(stream2_meter) == 0:
                    merged_data = stream1_meter.copy()
                else:
                    # Both streams have data - intelligent merge with deduplication
                    combined = pd.concat([stream1_meter, stream2_meter], ignore_index=True)
                    initial_count = len(combined)

                    # Remove exact duplicates based on timestamp and value
                    value_col = combined.columns[1]  # Second column is the meter value
                    combined = combined.drop_duplicates(subset=['TIMESTAMP', value_col], keep='first')

                    final_count = len(combined)
                    merge_stats['duplicates_removed'] += (initial_count - final_count)

                    merged_data = combined.sort_values('TIMESTAMP').reset_index(drop=True)

                if len(merged_data) > 0:
                    merged_vehicle_data[vehicle_id][meter_type] = merged_data
                    merge_stats['meters_merged'] += 1

        # Log merge statistics
        self.logger.info(f"✅ Stream Merge Completed:")
        self.logger.info(f"   • Vehicles processed: {merge_stats['vehicles_processed']}")
        self.logger.info(f"   • Meter datasets merged: {merge_stats['meters_merged']}")
        self.logger.info(f"   • Duplicate records removed: {merge_stats['duplicates_removed']:,}")

        return dict(merged_vehicle_data)