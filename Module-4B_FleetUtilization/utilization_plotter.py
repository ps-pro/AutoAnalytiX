"""
Utilization Analysis Plots

Extracted from original AutoAnalytiX FLEET_UTILIZATION_MODULE.plot_utilization_analysis() method.
Creates comprehensive utilization analysis visualization.
"""

import matplotlib.pyplot as plt
import traceback
from pathlib import Path
from .savings_projector import SavingsProjector


class UtilizationPlotter:
    """
    Utilization plotting functionality extracted from original FLEET_UTILIZATION_MODULE.
    """
    
    def __init__(self, logger, reports_dir):
        self.logger = logger
        self.reports_dir = Path(reports_dir)
        self.savings_projector = SavingsProjector(logger)

    def plot_utilization_analysis(self, vehicle_id, speed_data, idle_analysis, utilization_metrics):
        """Create comprehensive utilization analysis visualization"""
        if speed_data.empty:
            return

        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))

            # Plot 1: Speed Time Series with Idle Periods
            speed_sorted = speed_data.sort_values('TIMESTAMP')
            ax1.plot(speed_sorted['TIMESTAMP'], speed_sorted['speed'],
                    color='blue', alpha=0.7, linewidth=1, label='Speed')

            # Highlight idle periods
            for period in idle_analysis['idle_periods']:
                ax1.axvspan(period['start_time'], period['end_time'],
                           color='red', alpha=0.3, label='Idle Period' if period == idle_analysis['idle_periods'][0] else "")

            ax1.set_ylabel('Speed (mph)', fontweight='bold')
            ax1.set_title(f'{vehicle_id} - Speed Profile with Idle Periods', fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Plot 2: Utilization Pie Chart
            utilization_data = [utilization_metrics['utilization_percentage'], utilization_metrics['idle_percentage']]
            labels = [f"Active ({utilization_metrics['utilization_percentage']:.1f}%)",
                     f"Idle ({utilization_metrics['idle_percentage']:.1f}%)"]
            colors = ['green', 'red']

            ax2.pie(utilization_data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax2.set_title(f'{vehicle_id} - Time Utilization Breakdown', fontweight='bold')

            # Plot 3: Idle Cost Analysis
            cost_categories = ['Fuel Waste', 'Operational Cost']
            cost_values = [idle_analysis['fuel_waste_cost'], idle_analysis['operational_cost']]

            bars = ax3.bar(cost_categories, cost_values, color=['orange', 'red'], alpha=0.8, edgecolor='black')
            ax3.set_ylabel('Cost ($)', fontweight='bold')
            ax3.set_title(f'{vehicle_id} - Idle Cost Breakdown', fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar, value in zip(bars, cost_values):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + max(cost_values)*0.01,
                        f'${value:.2f}', ha='center', va='bottom', fontweight='bold')

            # Plot 4: Savings Potential
            savings_scenarios = self.savings_projector.calculate_savings_projections(idle_analysis)
            scenario_names = [data['description'] for data in savings_scenarios.values()]
            savings_values = [data['annual_savings'] for data in savings_scenarios.values()]

            bars = ax4.bar(range(len(scenario_names)), savings_values,
                          color=['lightgreen', 'green', 'darkgreen'], alpha=0.8, edgecolor='black')
            ax4.set_ylabel('Potential Annual Savings ($)', fontweight='bold')
            ax4.set_title(f'{vehicle_id} - Savings Potential from Idle Reduction', fontweight='bold')
            ax4.set_xticks(range(len(scenario_names)))
            ax4.set_xticklabels([name.split('(')[0] for name in scenario_names], rotation=45, ha='right')
            ax4.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar, value in zip(bars, savings_values):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + max(savings_values)*0.01,
                        f'${value:.0f}', ha='center', va='bottom', fontweight='bold')

            plt.tight_layout()

            # Save plot with error handling
            plot_path = self.reports_dir / "Plots" / "Utilization" / f"{vehicle_id}_utilization_analysis.pdf"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()

            # Verify plot creation
            self.logger.verify_plot_creation(plot_path, f"{vehicle_id} Utilization Analysis")

        except Exception as e:
            self.logger.error(f"❌ Failed to create utilization plot for {vehicle_id}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            plt.close('all')  # Ensure cleanup