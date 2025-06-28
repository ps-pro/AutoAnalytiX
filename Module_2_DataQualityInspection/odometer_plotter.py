"""
Odometer Analysis Plots

Extracted from original AutoAnalytiX DATAQUALITYINSPECTION_MODULE.plot_odometer_analysis() method.
Creates professional odometer analysis plots with moving averages.
"""

import matplotlib.pyplot as plt
import traceback
from pathlib import Path


class OdometerPlotter:
    """
    Odometer plotting functionality extracted from original DATAQUALITYINSPECTION_MODULE.
    """
    
    def __init__(self, logger, reports_dir):
        self.logger = logger
        self.reports_dir = Path(reports_dir)

    def plot_odometer_analysis(self, vehicle_id, odometer_analysis):
        """Create professional odometer analysis plots with moving averages"""
        if odometer_analysis is None:
            return

        try:
            odometer_data = odometer_analysis['raw_data']
            moving_averages = odometer_analysis['moving_averages']

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

            # Plot 1: Odometer Time Series with Moving Averages
            ax1.plot(odometer_data['TIMESTAMP'], odometer_data['odometer'],
                    color='blue', alpha=0.6, linewidth=1, label='Raw Odometer')

            # Plot moving averages
            colors = ['red', 'green', 'purple']
            for i, (ma_name, ma_data) in enumerate(moving_averages.items()):
                if len(ma_data.dropna()) > 0:
                    ax1.plot(odometer_data['TIMESTAMP'], ma_data,
                            color=colors[i % len(colors)], linewidth=2, label=ma_name)

            # Mark zero readings
            zero_readings = odometer_analysis['zero_readings']
            if len(zero_readings) > 0:
                ax1.scatter(zero_readings['TIMESTAMP'], zero_readings['odometer'],
                           color='red', marker='x', s=100, linewidth=3,
                           label=f'Zero Readings ({len(zero_readings)})')

            ax1.set_xlabel('Time', fontweight='bold')
            ax1.set_ylabel('Odometer Reading (miles)', fontweight='bold')
            ax1.set_title(f'{vehicle_id} - Odometer Time Series with Moving Averages', fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Plot 2: Odometer Change Distribution
            odometer_changes = odometer_data['odometer'].diff().dropna()
            increases = odometer_changes[odometer_changes >= 0]
            decreases = odometer_changes[odometer_changes < 0]

            if len(increases) > 0:
                ax2.hist(increases, bins=50, alpha=0.7, color='green',
                        label=f'Increases ({len(increases)})', density=True)

            if len(decreases) > 0:
                ax2.hist(decreases, bins=50, alpha=0.7, color='red',
                        label=f'Decreases ({len(decreases)})', density=True)

            ax2.axvline(0, color='black', linestyle='--', linewidth=2, label='Zero Change')
            ax2.set_xlabel('Odometer Change (miles)', fontweight='bold')
            ax2.set_ylabel('Density', fontweight='bold')
            ax2.set_title(f'{vehicle_id} - Odometer Change Distribution', fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save plot with error handling
            plot_path = self.reports_dir / "Plots" / "Odometer_Quality" / f"{vehicle_id}_odometer_analysis.pdf"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()

            # Verify plot creation
            self.logger.verify_plot_creation(plot_path, f"{vehicle_id} Odometer Analysis")

        except Exception as e:
            self.logger.error(f"❌ Failed to create odometer plot for {vehicle_id}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            plt.close('all')  # Ensure cleanup