"""
Raw Data Loading from Multiple Sources

Extracted from original AutoAnalytiX ETL_MODULE.load_raw_data() method.
Handles loading of telemetry datasets with progress tracking and validation.
"""

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
from shared.data_export import DataExporter


class DataLoader:
    """
    Raw data loading functionality extracted from original ETL_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.data_exporter = DataExporter(logger)
        self.processing_stats = {}
        self.data_lineage = []

    def load_raw_data(self, data_path):
        """Load and validate raw telematics data from multiple sources"""
        self.logger.log_module_start("1", "ETL Pipeline - Data Loading & Transformation")

        try:
            # Load datasets with progress tracking
            datasets = {}
            files_to_load = [
                ('telemetry_1.csv', 'telemetry_1'),
                ('telemetry_2.csv', 'telemetry_2'),
                ('vehicle_data.csv', 'vehicle_data')
            ]

            for filename, dataset_name in tqdm(files_to_load, desc="Loading datasets"):
                file_path = Path(data_path) / filename
                if not file_path.exists():
                    raise FileNotFoundError(f"Required file not found: {file_path}")

                datasets[dataset_name] = pd.read_csv(file_path)
                self.logger.info(f"✅ Loaded {dataset_name}: {datasets[dataset_name].shape[0]:,} records")

            # Export raw data summary
            self.export_raw_data_summary(datasets)

            # Log loading statistics
            self.processing_stats['raw_data_loaded'] = {
                'telemetry_1_records': len(datasets['telemetry_1']),
                'telemetry_2_records': len(datasets['telemetry_2']),
                'vehicle_count': len(datasets['vehicle_data']),
                'load_timestamp': datetime.now()
            }

            self.logger.info(f"📊 Data Loading Summary:")
            self.logger.info(f"   • Telemetry Stream 1: {datasets['telemetry_1'].shape[0]:,} records")
            self.logger.info(f"   • Telemetry Stream 2: {datasets['telemetry_2'].shape[0]:,} records")
            self.logger.info(f"   • Vehicle Master Data: {datasets['vehicle_data'].shape[0]} vehicles")

            return datasets

        except Exception as e:
            self.logger.error(f"❌ Error loading data: {e}")
            raise

    def export_raw_data_summary(self, datasets):
        """Export raw data summary for reference"""
        try:
            export_dir = Path("AutoAnalytiX__Reports") / "Data_Exports"
            
            summary = {
                'telemetry_1': {
                    'records': len(datasets['telemetry_1']),
                    'columns': datasets['telemetry_1'].columns.tolist(),
                    'date_range': {
                        'start': str(datasets['telemetry_1']['timestamp'].min()) if 'timestamp' in datasets['telemetry_1'].columns else 'N/A',
                        'end': str(datasets['telemetry_1']['timestamp'].max()) if 'timestamp' in datasets['telemetry_1'].columns else 'N/A'
                    }
                },
                'telemetry_2': {
                    'records': len(datasets['telemetry_2']),
                    'columns': datasets['telemetry_2'].columns.tolist(),
                    'date_range': {
                        'start': str(datasets['telemetry_2']['timestamp'].min()) if 'timestamp' in datasets['telemetry_2'].columns else 'N/A',
                        'end': str(datasets['telemetry_2']['timestamp'].max()) if 'timestamp' in datasets['telemetry_2'].columns else 'N/A'
                    }
                },
                'vehicle_data': {
                    'records': len(datasets['vehicle_data']),
                    'columns': datasets['vehicle_data'].columns.tolist()
                }
            }

            summary_path = export_dir / "raw_data_summary.json"
            self.data_exporter.export_to_json(summary, summary_path, "Raw Data Summary")

        except Exception as e:
            self.logger.error(f"Failed to export raw data summary: {e}")