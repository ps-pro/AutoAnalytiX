"""
Fuel Analysis Plots

Extracted from original AutoAnalytiX DATAQUALITYINSPECTION_MODULE.plot_fuel_analysis() method.
Creates professional fuel analysis plots.
"""

import matplotlib.pyplot as plt
import traceback
from pathlib import Path


class FuelPlotter:
    """
    Fuel plotting functionality extracted from original DATAQUALITYINSPECTION_MODULE.
    """
    
    def __init__(self, logger, reports_dir):
        self.logger = logger
        self.reports_dir = Path(reports_dir)

    def plot_fuel_analysis(self, vehicle_id, fuel_analysis):
        """Create professional fuel analysis plots"""
        if fuel_analysis is None:
            return

        try:
            fuel_data = fuel_analysis['raw_data']
            moving_averages = fuel_analysis['moving_averages']

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

            # Plot 1: Fuel Time Series with Moving Averages
            ax1.plot(fuel_data['TIMESTAMP'], fuel_data['fuel_level'],
                    color='blue', alpha=0.6, linewidth=1, label='Raw Fuel Level')

            # Plot moving averages
            colors = ['red', 'green']
            for i, (ma_name, ma_data) in enumerate(moving_averages.items()):
                if len(ma_data.dropna()) > 0:
                    ax1.plot(fuel_data['TIMESTAMP'], ma_data,
                            color=colors[i % len(colors)], linewidth=2, label=ma_name)

            # Mark range violations
            range_violations = fuel_analysis['range_violations']
            if len(range_violations) > 0:
                ax1.scatter(range_violations['TIMESTAMP'], range_violations['fuel_level'],
                           color='red', marker='s', s=50,
                           label=f'Range Violations ({len(range_violations)})')

            # Mark large drops
            large_drops = fuel_analysis['large_drops']
            if len(large_drops) > 0:
                ax1.scatter(large_drops['TIMESTAMP'], large_drops['fuel_level'],
                           color='orange', marker='v', s=80,
                           label=f'Large Drops ({len(large_drops)})')

            ax1.set_xlabel('Time', fontweight='bold')
            ax1.set_ylabel('Fuel Level (%)', fontweight='bold')
            ax1.set_title(f'{vehicle_id} - Fuel Level Time Series Analysis', fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Plot 2: Fuel Change Distribution
            fuel_changes = fuel_data['fuel_level'].diff().dropna()
            increases = fuel_changes[fuel_changes > 0]
            decreases = fuel_changes[fuel_changes <= 0]

            if len(decreases) > 0:
                ax2.hist(decreases, bins=50, alpha=0.7, color='red',
                        label=f'Decreases ({len(decreases)})', density=True)

            if len(increases) > 0:
                ax2.hist(increases, bins=50, alpha=0.7, color='green',
                        label=f'Increases ({len(increases)})', density=True)

            ax2.axvline(-20, color='darkred', linestyle='--', linewidth=2,
                       label='Large Drop Threshold (-20%)')
            ax2.set_xlabel('Fuel Level Change (%)', fontweight='bold')
            ax2.set_ylabel('Density', fontweight='bold')
            ax2.set_title(f'{vehicle_id} - Fuel Change Distribution Analysis', fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save plot with error handling
            plot_path = self.reports_dir / "Plots" / "Fuel_Quality" / f"{vehicle_id}_fuel_analysis.pdf"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()

            # Verify plot creation
            self.logger.verify_plot_creation(plot_path, f"{vehicle_id} Fuel Analysis")

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to create fuel plot for {vehicle_id}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            plt.close('all')  # Ensure cleanup