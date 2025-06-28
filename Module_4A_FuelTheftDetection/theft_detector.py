"""
Enhanced Theft Event Detection

Extracted from original AutoAnalytiX FUEL_THEFT_DETECTION_MODULE.detect_theft_events_enhanced() method.
Enhanced theft detection using cross-sensor validation and efficiency ratios.
"""

import pandas as pd


class TheftDetector:
    """
    Theft detection functionality extracted from original FUEL_THEFT_DETECTION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def detect_theft_events_enhanced(self, vehicle_id, mpg_data, rated_mpg):
        """Enhanced theft detection using cross-sensor validation and efficiency ratios"""
        theft_events = []

        # Focus on windows flagged for investigation
        suspicious_windows = mpg_data[mpg_data['mpg_validation'] == 'INVESTIGATE_POTENTIAL_THEFT']

        for idx, window in suspicious_windows.iterrows():
            if pd.isna(window['calculated_mpg']) or window['fuel_gallons_consumed'] <= 0:
                continue

            # Calculate efficiency ratio for threat assessment
            efficiency_ratio = window['calculated_mpg'] / rated_mpg if rated_mpg > 0 else 0

            # Determine threat level based on efficiency ratio
            if efficiency_ratio < 0.3:
                threat_level = "CRITICAL"
                priority = 1
            elif efficiency_ratio < 0.5:
                threat_level = "HIGH"
                priority = 1
            elif efficiency_ratio < 0.7:
                threat_level = "MEDIUM"
                priority = 2
            else:
                threat_level = "LOW"
                priority = 3

            # Calculate estimated theft value
            estimated_theft_gallons = window['fuel_gallons_consumed']
            estimated_theft_value = estimated_theft_gallons * 5.00  # $5.00 per gallon

            # Create comprehensive theft event record
            theft_event = {
                'vehicle_id': vehicle_id,
                'timestamp': window['timestamp'],
                'window_index': idx,
                'fuel_drop_percent': window['fuel_delta'],
                'fuel_gallons_consumed': window['fuel_gallons_consumed'],
                'distance_traveled': window['distance_delta'],
                'calculated_mpg': window['calculated_mpg'],
                'rated_mpg': rated_mpg,
                'efficiency_ratio': efficiency_ratio,
                'threat_level': threat_level,
                'investigation_priority': priority,
                'estimated_theft_value': estimated_theft_value,
                'time_window_hours': window['time_delta_hours'],
                'validation_flag': window['mpg_validation']
            }

            theft_events.append(theft_event)

            # Log theft event with detailed context
            self.logger.log_vehicle_violation(vehicle_id, "FUEL_THEFT_DETECTED", {
                "Violation Type": f"Potential Fuel Theft - {threat_level} PRIORITY",
                "Event Timestamp": str(window['timestamp']),
                "Fuel Consumed": f"{window['fuel_gallons_consumed']:.2f} gallons ({window['fuel_delta']:.1f}%)",
                "Distance Traveled": f"{window['distance_delta']:.1f} miles",
                "Calculated MPG": f"{window['calculated_mpg']:.1f}",
                "Rated MPG": f"{rated_mpg:.1f}",
                "Efficiency Ratio": f"{efficiency_ratio:.3f}",
                "Estimated Theft Value": f"${estimated_theft_value:.2f}",
                "Investigation Priority": priority,
                "Time Window": f"{window['time_delta_hours']:.1f} hours"
            })

        return theft_events