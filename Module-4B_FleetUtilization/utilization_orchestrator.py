"""
Utilization Analysis Coordination

Extracted from original AutoAnalytiX FLEET_UTILIZATION_MODULE.execute_utilization_analysis() method.
Orchestrates comprehensive fleet utilization analysis.
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm
from shared.data_export import DataExporter
from .idle_detector import IdleDetector
from .cost_calculator import CostCalculator
from .utilization_metrics import UtilizationMetrics
from .savings_projector import SavingsProjector
from .utilization_plotter import UtilizationPlotter


class FLEET_UTILIZATION_MODULE:
    """Fleet under-utilization detection and cost analysis with exports"""

    def __init__(self, cleaned_data, logger):
        self.cleaned_data = cleaned_data
        self.logger = logger
        self.utilization_analysis = {}
        self.reports_dir = self._setup_directories()
        
        # Initialize utilization components
        self.idle_detector = IdleDetector(logger)
        self.cost_calculator = CostCalculator(logger)
        self.utilization_metrics = UtilizationMetrics(logger)
        self.savings_projector = SavingsProjector(logger)
        self.utilization_plotter = UtilizationPlotter(logger, self.reports_dir)
        self.data_exporter = DataExporter(logger)

    def _setup_directories(self):
        """Setup directory structure for utilization analysis"""
        base_dir = Path("AutoAnalytiX__Reports")

        directories = [
            base_dir / "Utilization_Analysis",
            base_dir / "Plots" / "Utilization",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        return base_dir

    def export_utilization_data(self, vehicle_id, idle_analysis, utilization_metrics):
        """Export utilization analysis for Fleet Utilization module"""
        try:
            export_dir = self.reports_dir / "Utilization_Analysis"
            all_successful = True

            # Export idle periods if available
            if idle_analysis['idle_periods']:
                idle_df = pd.DataFrame(idle_analysis['idle_periods'])
                idle_path = export_dir / f"{vehicle_id}_idle_periods.csv"
                idle_df.to_csv(idle_path, index=False)
                self.logger.track_file_created(idle_path)

            # Export utilization summary
            summary_data = {
                'vehicle_id': [vehicle_id],
                'total_idle_hours': [idle_analysis['total_idle_hours']],
                'total_idle_cost': [idle_analysis['total_idle_cost']],
                'utilization_percentage': [utilization_metrics['utilization_percentage']],
                'efficiency_grade': [utilization_metrics['efficiency_grade']]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_path = export_dir / f"{vehicle_id}_utilization_summary.csv"
            summary_df.to_csv(summary_path, index=False)
            self.logger.track_file_created(summary_path)

            return all_successful

        except Exception as e:
            self.logger.error(f"Failed to export utilization data for {vehicle_id}: {e}")
            return False

    def execute_utilization_analysis(self):
        """Execute comprehensive fleet utilization analysis"""
        self.logger.log_module_start("4B", "Fleet Under-Utilization Detection & Cost Analysis")

        total_vehicles = len(self.cleaned_data)
        utilization_summary = {
            'vehicles_analyzed': 0,
            'total_idle_hours': 0,
            'total_idle_cost': 0,
            'vehicles_with_excessive_idle': 0,
            'potential_savings_50_percent': 0,
            'fleet_average_utilization': 0
        }

        utilization_scores = []

        # Process each vehicle for utilization analysis
        for vehicle_id, meters in tqdm(self.cleaned_data.items(),
                                     desc="Analyzing fleet utilization"):

            utilization_summary['vehicles_analyzed'] += 1

            # Get speed data for idle analysis
            speed_data = meters.get('speed', pd.DataFrame())
            if speed_data.empty:
                self.logger.warning(f"⚠️  {vehicle_id}: No speed data for utilization analysis")
                continue

            # Identify idle periods
            idle_periods = self.idle_detector.identify_idle_periods(vehicle_id, speed_data)

            # Calculate idle costs
            idle_analysis = self.cost_calculator.calculate_idle_costs(vehicle_id, idle_periods)

            # Calculate utilization metrics
            utilization_metrics = self.utilization_metrics.calculate_utilization_metrics(vehicle_id, speed_data, idle_analysis)

            # Store comprehensive analysis
            self.utilization_analysis[vehicle_id] = {
                'idle_analysis': idle_analysis,
                'utilization_metrics': utilization_metrics,
                'savings_projections': self.savings_projector.calculate_savings_projections(idle_analysis)
            }

            # Export utilization data
            self.export_utilization_data(vehicle_id, idle_analysis, utilization_metrics)

            # Update fleet summary
            utilization_summary['total_idle_hours'] += idle_analysis['total_idle_hours']
            utilization_summary['total_idle_cost'] += idle_analysis['total_idle_cost']
            utilization_summary['potential_savings_50_percent'] += idle_analysis['total_idle_cost'] * 0.50

            if idle_analysis['total_idle_cost'] > 200:  # Threshold for excessive idle
                utilization_summary['vehicles_with_excessive_idle'] += 1

            if utilization_metrics:
                utilization_scores.append(utilization_metrics['utilization_percentage'])

            # Generate utilization plot
            self.utilization_plotter.plot_utilization_analysis(vehicle_id, speed_data, idle_analysis, utilization_metrics)

            # Log vehicle utilization summary
            if idle_analysis['total_idle_cost'] > 50:  # Log significant idle costs
                self.logger.info(f"💰 {vehicle_id}: {idle_analysis['total_idle_hours']:.1f} idle hours, "
                               f"${idle_analysis['total_idle_cost']:.2f} cost, "
                               f"{utilization_metrics.get('utilization_percentage', 0):.1f}% utilization")

        # Calculate fleet averages
        if utilization_scores:
            utilization_summary['fleet_average_utilization'] = sum(utilization_scores) / len(utilization_scores)

        # Generate comprehensive utilization summary
        self.logger.info("✅ Fleet Utilization Analysis Completed")
        self.logger.info(f"💰 Utilization Summary:")
        self.logger.info(f"   • Vehicles analyzed: {utilization_summary['vehicles_analyzed']}")
        self.logger.info(f"   • Total idle hours: {utilization_summary['total_idle_hours']:.1f}")
        self.logger.info(f"   • Total idle cost: ${utilization_summary['total_idle_cost']:,.2f}")
        self.logger.info(f"   • Vehicles with excessive idle: {utilization_summary['vehicles_with_excessive_idle']}")
        self.logger.info(f"   • Fleet average utilization: {utilization_summary['fleet_average_utilization']:.1f}%")
        self.logger.info(f"   • Potential savings (50% reduction): ${utilization_summary['potential_savings_50_percent']:,.2f}")

        return self.utilization_analysis, utilization_summary