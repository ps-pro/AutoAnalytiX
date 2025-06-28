"""
Main ETL Pipeline Coordination

Extracted from original AutoAnalytiX ETL_MODULE class.
Orchestrates the complete ETL pipeline with comprehensive logging.
"""

from datetime import datetime
from .data_loader import DataLoader
from .timestamp_processor import TimestampProcessor
from .stream1_extractor import Stream1Extractor
from .stream2_extractor import Stream2Extractor
from .data_merger import DataMerger


class ETL_MODULE:
    """Enhanced ETL pipeline with data export capabilities"""

    def __init__(self, logger):
        self.logger = logger
        self.processing_stats = {}
        self.data_lineage = []
        
        # Initialize ETL components
        self.data_loader = DataLoader(logger)
        self.timestamp_processor = TimestampProcessor(logger)
        self.stream1_extractor = Stream1Extractor(logger)
        self.stream2_extractor = Stream2Extractor(logger)
        self.data_merger = DataMerger(logger)

    def execute_etl_pipeline(self, data_path):
        """Execute complete ETL pipeline with comprehensive logging"""
        try:
            # Load raw datasets
            raw_data = self.data_loader.load_raw_data(data_path)

            # Standardize timestamps across all sources
            self.logger.info("🕐 Standardizing timestamps across all data sources")
            tel1_clean = self.timestamp_processor.standardize_timestamps(raw_data['telemetry_1'])
            tel2_clean = self.timestamp_processor.standardize_timestamps(raw_data['telemetry_2'])

            # Extract meter data preserving natural sensor frequencies
            stream1_meter_data = self.stream1_extractor.extract_meter_data_from_stream1(tel1_clean)
            stream2_meter_data = self.stream2_extractor.extract_meter_data_from_stream2(tel2_clean)

            # Intelligent merge with deduplication
            final_vehicle_meter_data = self.data_merger.merge_meter_data_streams(stream1_meter_data, stream2_meter_data)

            # Generate ETL summary statistics
            etl_summary = {
                'total_vehicles': len(final_vehicle_meter_data),
                'total_speed_datasets': sum(1 for v in final_vehicle_meter_data.values() if 'speed' in v),
                'total_odometer_datasets': sum(1 for v in final_vehicle_meter_data.values() if 'odometer' in v),
                'total_fuel_datasets': sum(1 for v in final_vehicle_meter_data.values() if 'fuel' in v),
                'processing_timestamp': datetime.now()
            }

            self.logger.info("[OK] ETL Pipeline Completed Successfully")
            self.logger.info(f"📊 ETL Summary: {etl_summary['total_vehicles']} vehicles processed")

            return {
                'vehicle_meter_data': final_vehicle_meter_data,
                'vehicle_metadata': raw_data['vehicle_data'],
                'etl_summary': etl_summary
            }

        except Exception as e:
            self.logger.error(f"[ERROR] ETL Pipeline failed: {e}")
            raise