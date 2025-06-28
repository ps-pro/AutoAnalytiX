"""
Theft Detection Coordination

Extracted from original AutoAnalytiX FUEL_THEFT_DETECTION_MODULE.execute_theft_detection() method.
Orchestrates comprehensive fuel theft detection analysis.
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
from shared.data_export import DataExporter
from .time_synchronizer import TimeSynchronizer
from .mpg_calculator import MPGCalculator
from .theft_detector import TheftDetector
from .theft_plotter import TheftPlotter


class FUEL_THEFT_DETECTION_MODULE:
    """Advanced fuel theft detection with robust plotting and exports"""

    def __init__(self, cleaned_data, vehicle_metadata, logger):
        self.cleaned_data = cleaned_data
        self.vehicle_metadata = vehicle_metadata
        self.logger = logger
        self.theft_events = {}
        self.synchronized_data = {}
        self.reports_dir = self._setup_directories()
        
        # Initialize detection components
        self.time_synchronizer = TimeSynchronizer(logger)
        self.mpg_calculator = MPGCalculator(logger)
        self.theft_detector = TheftDetector(logger)
        self.theft_plotter = TheftPlotter(logger, self.reports_dir)
        self.data_exporter = DataExporter(logger)

    def _setup_directories(self):
        """Setup directory structure for theft detection analysis"""
        base_dir = Path("AutoAnalytiX__Reports")

        directories = [
            base_dir / "Theft_Detection",
            base_dir / "Synchronized_Data",
            base_dir / "Plots" / "Theft_Analysis",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        return base_dir

    def export_synchronized_data(self, vehicle_id, sync_data):
        """Export synchronized data to CSV"""
        try:
            export_path = self.reports_dir / "Synchronized_Data" / f"{vehicle_id}_synchronized_10min.csv"
            sync_data.to_csv(export_path, index=False)
            self.logger.track_file_created(export_path)
        except Exception as e:
            self.logger.error(f"Failed to export synchronized data for {vehicle_id}: {e}")

    def export_theft_events(self, vehicle_id, theft_events):
        """Export theft events to CSV"""
        if theft_events:
            try:
                df = pd.DataFrame(theft_events)
                export_path = self.reports_dir / "Theft_Detection" / f"{vehicle_id}_theft_events.csv"
                df.to_csv(export_path, index=False)
                self.logger.track_file_created(export_path)
            except Exception as e:
                self.logger.error(f"Failed to export theft events for {vehicle_id}: {e}")

    def execute_theft_detection(self):
        """Execute comprehensive fuel theft detection analysis"""
        self.logger.log_module_start("4A", "Fuel Theft Detection - Cross-Sensor Validation")

        total_vehicles = len(self.cleaned_data)
        theft_summary = {
            'vehicles_analyzed': 0,
            'vehicles_with_theft_events': 0,
            'total_theft_events': 0,
            'total_estimated_loss': 0.0,
            'high_priority_events': 0
        }

        # Process each vehicle for theft detection with progress tracking
        for vehicle_id, meters in tqdm(self.cleaned_data.items(),
                                     desc="Analyzing vehicles for theft",
                                     total=total_vehicles):

            theft_summary['vehicles_analyzed'] += 1

            # Get vehicle specifications
            vehicle_spec = self.vehicle_metadata[self.vehicle_metadata['id'] == vehicle_id]
            if vehicle_spec.empty:
                self.logger.warning(f"⚠️  {vehicle_id}: Vehicle specifications not found")
                continue

            tank_capacity = vehicle_spec['tank_capacity'].iloc[0]
            rated_mpg = vehicle_spec['rated_mpg'].iloc[0]

            # Get cleaned meter data
            fuel_data = meters.get('fuel', pd.DataFrame())
            odometer_data = meters.get('odometer', pd.DataFrame())
            speed_data = meters.get('speed', pd.DataFrame())

            # Skip if insufficient data for analysis
            if fuel_data.empty or odometer_data.empty:
                self.logger.warning(f"⚠️  {vehicle_id}: Insufficient data for theft analysis")
                continue

            # Create 10-minute synchronized windows
            sync_data = self.time_synchronizer.create_10_minute_synchronized_windows(
                vehicle_id, fuel_data, odometer_data, speed_data
            )

            if sync_data.empty:
                self.logger.warning(f"⚠️  {vehicle_id}: No synchronized data windows created")
                continue

            # Store synchronized data for potential export
            self.synchronized_data[vehicle_id] = sync_data

            # Calculate real-time MPG with physics validation
            mpg_data = self.mpg_calculator.calculate_real_time_mpg(vehicle_id, sync_data, tank_capacity)

            # Detect theft events using enhanced cross-sensor validation
            theft_events = self.theft_detector.detect_theft_events_enhanced(vehicle_id, mpg_data, rated_mpg)

            if theft_events:
                self.theft_events[vehicle_id] = theft_events
                theft_summary['vehicles_with_theft_events'] += 1
                theft_summary['total_theft_events'] += len(theft_events)

                # Calculate financial impact
                vehicle_loss = sum(event['estimated_theft_value'] for event in theft_events)
                theft_summary['total_estimated_loss'] += vehicle_loss

                # Count high priority events
                high_priority = sum(1 for event in theft_events if event['investigation_priority'] == 1)
                theft_summary['high_priority_events'] += high_priority

                # Export theft events
                self.export_theft_events(vehicle_id, theft_events)

                self.logger.info(f"🚨 {vehicle_id}: {len(theft_events)} theft events detected, "
                               f"${vehicle_loss:.2f} estimated loss")
            else:
                self.logger.debug(f"[OK] {vehicle_id}: No theft events detected")

            # Export synchronized data
            self.export_synchronized_data(vehicle_id, sync_data)

            # Generate theft analysis plot
            self.theft_plotter.plot_theft_analysis(vehicle_id, mpg_data, theft_events)

        # Generate comprehensive theft detection summary
        self.logger.info("[OK] Fuel Theft Detection Analysis Completed")
        self.logger.info(f"🚨 Theft Detection Summary:")
        self.logger.info(f"   • Vehicles analyzed: {theft_summary['vehicles_analyzed']}")
        self.logger.info(f"   • Vehicles with theft events: {theft_summary['vehicles_with_theft_events']}")
        self.logger.info(f"   • Total theft events: {theft_summary['total_theft_events']}")
        self.logger.info(f"   • Total estimated loss: ${theft_summary['total_estimated_loss']:,.2f}")
        self.logger.info(f"   • High priority events: {theft_summary['high_priority_events']}")

        return self.theft_events, theft_summary