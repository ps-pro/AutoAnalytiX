"""
Theft Analysis Visualizations

Extracted from original AutoAnalytiX FUEL_THEFT_DETECTION_MODULE.plot_theft_analysis() method.
Creates comprehensive theft analysis visualization with error handling.
"""

import matplotlib.pyplot as plt
import pandas as pd
import traceback
from pathlib import Path


class TheftPlotter:
    """
    Theft plotting functionality extracted from original FUEL_THEFT_DETECTION_MODULE.
    """
    
    def __init__(self, logger, reports_dir):
        self.logger = logger
        self.reports_dir = Path(reports_dir)

    def plot_theft_analysis(self, vehicle_id, mpg_data, theft_events):
        """Create comprehensive theft analysis visualization with error handling"""
        if mpg_data.empty:
            return

        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))

            # Plot 1: Fuel Level Time Series with Theft Events
            ax1.plot(mpg_data['timestamp'], mpg_data['fuel_level'],
                    color='blue', linewidth=2, label='Fuel Level (%)')

            # Mark theft events
            if theft_events:
                threat_colors = {'CRITICAL': 'darkred', 'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'yellow'}
                for event in theft_events:
                    event_time = event['timestamp']
                    event_fuel = mpg_data[mpg_data['timestamp'] == event_time]['fuel_level'].iloc[0]
                    color = threat_colors.get(event['threat_level'], 'gray')
                    ax1.scatter(event_time, event_fuel, c=color, s=200, marker='X',
                               edgecolors='black', linewidth=1,
                               label=f"{event['threat_level']} Theft" if event == theft_events[0] else "")

            ax1.set_ylabel('Fuel Level (%)', fontweight='bold')
            ax1.set_title(f'{vehicle_id} - Fuel Level with Theft Events', fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Plot 2: Real-time MPG Calculation
            valid_mpg = mpg_data[mpg_data['calculated_mpg'].notna()]
            if not valid_mpg.empty:
                ax2.plot(valid_mpg['timestamp'], valid_mpg['calculated_mpg'],
                        color='green', linewidth=2, marker='o', label='Calculated MPG')

                # Add rated MPG baseline
                if len(theft_events) > 0:
                    rated_mpg = theft_events[0]['rated_mpg']
                    ax2.axhline(rated_mpg, color='blue', linestyle='--', linewidth=2,
                               label=f'Rated MPG ({rated_mpg:.1f})')

                # Mark physics validation thresholds
                ax2.axhline(50, color='red', linestyle='--', alpha=0.7, label='Sensor Error Threshold (50 MPG)')
                ax2.axhline(2, color='orange', linestyle='--', alpha=0.7, label='Theft Investigation Threshold (2 MPG)')

            ax2.set_ylabel('Miles Per Gallon', fontweight='bold')
            ax2.set_title(f'{vehicle_id} - Real-time MPG Analysis', fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            # Plot 3: Odometer Distance Progression
            ax3.plot(mpg_data['timestamp'], mpg_data['odometer'],
                    color='purple', linewidth=2, label='Odometer Reading')
            ax3.set_ylabel('Odometer (miles)', fontweight='bold')
            ax3.set_title(f'{vehicle_id} - Distance Progression', fontweight='bold')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

            # Plot 4: Theft Event Summary
            if theft_events:
                threat_levels = [event['threat_level'] for event in theft_events]
                level_counts = pd.Series(threat_levels).value_counts()

                colors = ['darkred', 'red', 'orange', 'yellow']
                bars = ax4.bar(level_counts.index, level_counts.values,
                              color=colors[:len(level_counts)], alpha=0.8, edgecolor='black')

                ax4.set_ylabel('Number of Events', fontweight='bold')
                ax4.set_title(f'{vehicle_id} - Theft Events by Threat Level', fontweight='bold')
                ax4.grid(True, alpha=0.3, axis='y')

                # Add value labels on bars
                for bar, count in zip(bars, level_counts.values):
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            str(count), ha='center', va='bottom', fontweight='bold')
            else:
                ax4.text(0.5, 0.5, 'No Theft Events Detected',
                        transform=ax4.transAxes, ha='center', va='center',
                        fontsize=16, fontweight='bold')
                ax4.set_title(f'{vehicle_id} - No Theft Events', fontweight='bold')

            plt.tight_layout()

            # Save plot with error handling
            plot_path = self.reports_dir / "Plots" / "Theft_Analysis" / f"{vehicle_id}_theft_analysis.pdf"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()

            # Verify plot creation
            self.logger.verify_plot_creation(plot_path, f"{vehicle_id} Theft Analysis")

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to create theft plot for {vehicle_id}: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            plt.close('all')  # Ensure cleanup