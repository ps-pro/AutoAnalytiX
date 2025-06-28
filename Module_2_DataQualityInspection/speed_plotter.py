"""
Speed Analysis Visualizations

Extracted from original AutoAnalytiX DATAQUALITYINSPECTION_MODULE.plot_speed_analysis() method.
Creates professional speed analysis plots with error handling.
"""

import matplotlib.pyplot as plt
import traceback
from pathlib import Path


class SpeedPlotter:
    """
    Speed plotting functionality extracted from original DATAQUALITYINSPECTION_MODULE.
    """
    
    def __init__(self, logger, reports_dir):
        self.logger = logger
        self.reports_dir = Path(reports_dir)

    def plot_speed_analysis(self, vehicle_id, speed_analysis):
        """Create professional speed analysis plots with error handling"""
        if speed_analysis is None:
            return

        try:
            # Create acceleration distribution plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

            # Plot 1: Acceleration Distribution
            accelerations = speed_analysis['valid_accelerations']
            n, bins, patches = ax1.hist(accelerations, bins=50, alpha=0.7, color='skyblue',
                                       edgecolor='black', linewidth=0.5, density=True)

            # Add statistical overlays
            ax1.axvline(speed_analysis['statistics']['mean_acceleration'], color='green',
                       linestyle='-', linewidth=2,
                       label=f"Mean: {speed_analysis['statistics']['mean_acceleration']:.1f} mph/min")
            ax1.axvline(speed_analysis['statistics']['percentile_95'], color='orange',
                       linestyle='-', linewidth=2,
                       label=f"95th Percentile: {speed_analysis['statistics']['percentile_95']:.1f} mph/min")
            ax1.axvline(30, color='red', linestyle='--', linewidth=2,
                       label='Critical Threshold (30 mph/min)')

            ax1.set_xlabel('Acceleration (mph/min)', fontweight='bold')
            ax1.set_ylabel('Density', fontweight='bold')
            ax1.set_title(f'{vehicle_id} - Speed Acceleration Distribution Analysis', fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Plot 2: Threshold Impact Analysis
            thresholds = list(speed_analysis['threshold_analysis'].keys())
            violations = [speed_analysis['threshold_analysis'][t]['violations'] for t in thresholds]
            percentages = [speed_analysis['threshold_analysis'][t]['percentage'] for t in thresholds]

            bars = ax2.bar(thresholds, violations, alpha=0.7, color='coral',
                          edgecolor='black', linewidth=0.5, label='Violation Count')

            ax2_twin = ax2.twinx()
            line = ax2_twin.plot(thresholds, percentages, color='darkred', marker='o',
                               linewidth=3, markersize=8, label='Violation %')

            ax2.set_xlabel('Acceleration Threshold (mph/min)', fontweight='bold')
            ax2.set_ylabel('Number of Violations', color='coral', fontweight='bold')
            ax2_twin.set_ylabel('Percentage of Data (%)', color='darkred', fontweight='bold')
            ax2.set_title(f'{vehicle_id} - Acceleration Threshold Impact Analysis', fontweight='bold')

            # Combine legends
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save plot with error handling
            plot_path = self.reports_dir / "Plots" / "Speed_Quality" / f"{vehicle_id}_speed_analysis.pdf"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()

            # Verify plot creation
            self.logger.verify_plot_creation(plot_path, f"{vehicle_id} Speed Analysis")

        except Exception as e:
            self.logger.error(f"❌ Failed to create speed plot for {vehicle_id}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            plt.close('all')  # Ensure cleanup