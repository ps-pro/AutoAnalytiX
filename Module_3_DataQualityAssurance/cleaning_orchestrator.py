"""
Data Cleaning Coordination

Extracted from original AutoAnalytiX DATAQUALITYASSURANCE_MODULE.execute_data_cleaning() method.
Orchestrates systematic data cleaning across all vehicles.
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
from datetime import datetime
from shared.data_export import DataExporter
from speed_cleaner import SpeedCleaner
from odometer_cleaner import OdometerCleaner
from fuel_cleaner import FuelCleaner
from quality_reporter import QualityReporter


class DATAQUALITYASSURANCE_MODULE:
    """Systematic data cleaning with CSV exports"""

    def __init__(self, vehicle_meter_data, quality_issues, logger):
        self.vehicle_meter_data = vehicle_meter_data
        self.quality_issues = quality_issues
        self.logger = logger
        self.cleaned_data = {}
        self.cleaning_stats = {}
        self.reports_dir = self._setup_directories()
        
        # Initialize cleaning components
        self.speed_cleaner = SpeedCleaner(logger)
        self.odometer_cleaner = OdometerCleaner(logger)
        self.fuel_cleaner = FuelCleaner(logger)
        self.quality_reporter = QualityReporter(logger, self.reports_dir)
        self.data_exporter = DataExporter(logger)

    def _setup_directories(self):
        """Setup directory structure for data quality assurance"""
        base_dir = Path("AutoAnalytiX__Reports")

        directories = [
            base_dir / "Quality_Reports" / "Before_After",
            base_dir / "Cleaned_Data_Exports"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        return base_dir

    def export_cleaned_data(self, vehicle_id, cleaned_vehicle_data):
        """Export cleaned data to CSV files"""
        try:
            export_dir = self.reports_dir / "Cleaned_Data_Exports"

            for meter_type, meter_data in cleaned_vehicle_data.items():
                if not meter_data.empty:
                    csv_path = export_dir / f"{vehicle_id}_{meter_type}_cleaned.csv"
                    meter_data.to_csv(csv_path, index=False)
                    self.logger.track_file_created(csv_path)

        except Exception as e:
            self.logger.error(f"Failed to export cleaned data for {vehicle_id}: {e}")

    def execute_data_cleaning(self):
        """Execute comprehensive data cleaning across all vehicles"""
        self.logger.log_module_start("3", "Data Quality Assurance - Systematic Data Cleaning")

        total_vehicles = len(self.vehicle_meter_data)
        fleet_cleaning_summary = {
            'vehicles_processed': 0,
            'total_records_cleaned': 0,
            'total_records_retained': 0,
            'vehicles_requiring_significant_cleaning': 0,
            'csv_files_exported': 0
        }

        # Process each vehicle's data systematically
        for vehicle_id, meters in tqdm(self.vehicle_meter_data.items(),
                                     desc="Cleaning vehicle data"):

            fleet_cleaning_summary['vehicles_processed'] += 1
            vehicle_cleaning_stats = {}
            cleaned_vehicle_data = {}

            # Get quality issues for this vehicle
            vehicle_quality_issues = self.quality_issues.get(vehicle_id, {})

            # Clean Speed Data
            speed_data = meters.get('speed', pd.DataFrame())
            if not speed_data.empty:
                speed_issues = vehicle_quality_issues.get('speed', {})
                cleaned_speed, speed_stats = self.speed_cleaner.clean_speed_data(vehicle_id, speed_data, speed_issues)
                cleaned_vehicle_data['speed'] = cleaned_speed
                vehicle_cleaning_stats['speed'] = speed_stats

            # Clean Odometer Data
            odometer_data = meters.get('odometer', pd.DataFrame())
            if not odometer_data.empty:
                odometer_issues = vehicle_quality_issues.get('odometer', {})
                cleaned_odometer, odometer_stats = self.odometer_cleaner.clean_odometer_data(vehicle_id, odometer_data, odometer_issues)
                cleaned_vehicle_data['odometer'] = cleaned_odometer
                vehicle_cleaning_stats['odometer'] = odometer_stats

            # Clean Fuel Data
            fuel_data = meters.get('fuel', pd.DataFrame())
            if not fuel_data.empty:
                fuel_issues = vehicle_quality_issues.get('fuel', {})
                cleaned_fuel, fuel_stats = self.fuel_cleaner.clean_fuel_data(vehicle_id, fuel_data, fuel_issues)
                cleaned_vehicle_data['fuel'] = cleaned_fuel
                vehicle_cleaning_stats['fuel'] = fuel_stats

            # Export cleaned data to CSV files
            self.export_cleaned_data(vehicle_id, cleaned_vehicle_data)
            fleet_cleaning_summary['csv_files_exported'] += len(cleaned_vehicle_data)

            # Store cleaned data
            self.cleaned_data[vehicle_id] = cleaned_vehicle_data
            self.cleaning_stats[vehicle_id] = vehicle_cleaning_stats

            # Generate quality report for this vehicle
            self.quality_reporter.generate_quality_report(vehicle_id, vehicle_cleaning_stats)

            # Update fleet statistics
            vehicle_total_initial = sum(stats.get('initial_records', 0) for stats in vehicle_cleaning_stats.values())
            vehicle_total_final = sum(stats.get('final_records', 0) for stats in vehicle_cleaning_stats.values())

            fleet_cleaning_summary['total_records_cleaned'] += (vehicle_total_initial - vehicle_total_final)
            fleet_cleaning_summary['total_records_retained'] += vehicle_total_final

            if (vehicle_total_initial - vehicle_total_final) > (vehicle_total_initial * 0.05):
                fleet_cleaning_summary['vehicles_requiring_significant_cleaning'] += 1

        # Generate fleet-wide cleaning summary
        total_initial_fleet = fleet_cleaning_summary['total_records_retained'] + fleet_cleaning_summary['total_records_cleaned']
        fleet_retention_rate = fleet_cleaning_summary['total_records_retained'] / total_initial_fleet * 100 if total_initial_fleet > 0 else 0

        self.logger.info("✅ Data Quality Assurance Completed")
        self.logger.info(f"📊 Fleet Cleaning Summary:")
        self.logger.info(f"   • Vehicles processed: {fleet_cleaning_summary['vehicles_processed']}")
        self.logger.info(f"   • Records cleaned: {fleet_cleaning_summary['total_records_cleaned']:,}")
        self.logger.info(f"   • Records retained: {fleet_cleaning_summary['total_records_retained']:,}")
        self.logger.info(f"   • Fleet retention rate: {fleet_retention_rate:.1f}%")
        self.logger.info(f"   • Vehicles requiring significant cleaning: {fleet_cleaning_summary['vehicles_requiring_significant_cleaning']}")
        self.logger.info(f"   • CSV files exported: {fleet_cleaning_summary['csv_files_exported']}")

        return self.cleaned_data