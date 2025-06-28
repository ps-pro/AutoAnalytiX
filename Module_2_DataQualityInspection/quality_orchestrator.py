"""
Quality Inspection Coordination

Extracted from original AutoAnalytiX DATAQUALITYINSPECTION_MODULE.execute_quality_inspection() method.
Orchestrates comprehensive data quality inspection across all vehicles.
"""

from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
from .speed_analyzer import SpeedAnalyzer
from .odometer_analyzer import OdometerAnalyzer
from .fuel_analyzer import FuelAnalyzer
from .speed_plotter import SpeedPlotter
from .odometer_plotter import OdometerPlotter
from .fuel_plotter import FuelPlotter


class DATAQUALITYINSPECTION_MODULE:
    """Advanced data quality inspection with individual sensor analysis"""

    def __init__(self, vehicle_meter_data, vehicle_metadata, logger):
        self.vehicle_meter_data = vehicle_meter_data
        self.vehicle_metadata = vehicle_metadata
        self.logger = logger
        self.quality_issues = defaultdict(dict)
        self.reports_dir = self._setup_directories()
        
        # Initialize analysis components
        self.speed_analyzer = SpeedAnalyzer(logger)
        self.odometer_analyzer = OdometerAnalyzer(logger)
        self.fuel_analyzer = FuelAnalyzer(logger)
        
        # Initialize plotting components
        self.speed_plotter = SpeedPlotter(logger, self.reports_dir)
        self.odometer_plotter = OdometerPlotter(logger, self.reports_dir)
        self.fuel_plotter = FuelPlotter(logger, self.reports_dir)

    def _setup_directories(self):
        """Setup organized directory structure for quality inspection"""
        base_dir = Path("AutoAnalytiX__Reports")

        directories = [
            base_dir / "Plots" / "Speed_Quality",
            base_dir / "Plots" / "Odometer_Quality",
            base_dir / "Plots" / "Fuel_Quality"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        return base_dir

    def execute_quality_inspection(self):
        """Execute comprehensive data quality inspection across all vehicles"""
        self.logger.log_module_start("2", "Data Quality Inspection - Individual Sensor Analysis")

        total_vehicles = len(self.vehicle_meter_data)
        inspection_summary = {
            'vehicles_processed': 0,
            'speed_analyses': 0,
            'odometer_analyses': 0,
            'fuel_analyses': 0,
            'quality_issues_detected': 0,
            'plots_created': 0
        }

        # Process each vehicle individually
        for vehicle_id, meters in tqdm(self.vehicle_meter_data.items(),
                                     desc="Inspecting vehicle data quality"):

            inspection_summary['vehicles_processed'] += 1
            vehicle_issues = {}

            # Speed Quality Analysis
            speed_data = meters.get('speed', None)
            if speed_data is not None and len(speed_data) > 0:
                speed_analysis = self.speed_analyzer.analyze_speed_patterns(vehicle_id, speed_data)
                if speed_analysis:
                    self.quality_issues[vehicle_id]['speed'] = speed_analysis
                    self.speed_plotter.plot_speed_analysis(vehicle_id, speed_analysis)
                    inspection_summary['speed_analyses'] += 1
                    inspection_summary['plots_created'] += 1
                    vehicle_issues['speed_quality_score'] = speed_analysis['data_quality_score']

            # Odometer Quality Analysis
            odometer_data = meters.get('odometer', None)
            if odometer_data is not None and len(odometer_data) > 0:
                odometer_analysis = self.odometer_analyzer.analyze_odometer_patterns(vehicle_id, odometer_data)
                if odometer_analysis:
                    self.quality_issues[vehicle_id]['odometer'] = odometer_analysis
                    self.odometer_plotter.plot_odometer_analysis(vehicle_id, odometer_analysis)
                    inspection_summary['odometer_analyses'] += 1
                    inspection_summary['plots_created'] += 1
                    vehicle_issues['odometer_quality_score'] = odometer_analysis['data_quality_score']

            # Fuel Quality Analysis
            fuel_data = meters.get('fuel', None)
            if fuel_data is not None and len(fuel_data) > 0:
                fuel_analysis = self.fuel_analyzer.analyze_fuel_patterns(vehicle_id, fuel_data)
                if fuel_analysis:
                    self.quality_issues[vehicle_id]['fuel'] = fuel_analysis
                    self.fuel_plotter.plot_fuel_analysis(vehicle_id, fuel_analysis)
                    inspection_summary['fuel_analyses'] += 1
                    inspection_summary['plots_created'] += 1
                    vehicle_issues['fuel_quality_score'] = fuel_analysis['data_quality_score']

            # Log quality report for this vehicle
            if vehicle_issues:
                self.logger.log_quality_report("DataQualityInspection", vehicle_id, vehicle_issues)
                inspection_summary['quality_issues_detected'] += 1

        # Generate comprehensive inspection summary
        self.logger.info("[OK] Data Quality Inspection Completed")
        self.logger.info(f"📊 Inspection Summary:")
        self.logger.info(f"   • Vehicles processed: {inspection_summary['vehicles_processed']}")
        self.logger.info(f"   • Speed analyses: {inspection_summary['speed_analyses']}")
        self.logger.info(f"   • Odometer analyses: {inspection_summary['odometer_analyses']}")
        self.logger.info(f"   • Fuel analyses: {inspection_summary['fuel_analyses']}")
        self.logger.info(f"   • Vehicles with quality issues: {inspection_summary['quality_issues_detected']}")
        self.logger.info(f"   • Plots created: {inspection_summary['plots_created']}")

        return self.quality_issues