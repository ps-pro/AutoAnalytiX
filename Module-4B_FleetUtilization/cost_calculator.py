"""
Idle Cost Calculations ($34/hour)

Extracted from original AutoAnalytiX FLEET_UTILIZATION_MODULE.calculate_idle_costs() method.
Calculates idle costs using the specified formula.
"""


class CostCalculator:
    """
    Cost calculation functionality extracted from original FLEET_UTILIZATION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def calculate_idle_costs(self, vehicle_id, idle_periods):
        """Calculate idle costs using the specified formula"""
        if not idle_periods:
            return {
                'total_idle_hours': 0,
                'total_idle_cost': 0,
                'fuel_waste_cost': 0,
                'operational_cost': 0,
                'idle_events': 0,
                'longest_idle_hours': 0,
                'average_idle_duration': 0
            }

        # Calculate total idle time
        total_idle_hours = sum(period['duration_hours'] for period in idle_periods)

        # Apply specified cost formula: Idle_Hours × $34/hour
        fuel_waste_cost = total_idle_hours * 4.00  # $4/hour for fuel waste
        operational_cost = total_idle_hours * 30.00  # $30/hour for operational cost
        total_idle_cost = total_idle_hours * 34.00  # Combined cost

        # Calculate additional statistics
        idle_durations = [period['duration_hours'] for period in idle_periods]
        longest_idle = max(idle_durations) if idle_durations else 0
        average_idle = sum(idle_durations) / len(idle_durations) if idle_durations else 0

        cost_analysis = {
            'total_idle_hours': total_idle_hours,
            'total_idle_cost': total_idle_cost,
            'fuel_waste_cost': fuel_waste_cost,
            'operational_cost': operational_cost,
            'idle_events': len(idle_periods),
            'longest_idle_hours': longest_idle,
            'average_idle_duration': average_idle,
            'cost_per_hour': 34.00,
            'idle_periods': idle_periods
        }

        # Log significant idle costs
        if total_idle_cost > 100:  # Significant cost threshold
            self.logger.log_vehicle_violation(vehicle_id, "EXCESSIVE_IDLE_COST", {
                "Violation Type": "High Idle Cost Detected",
                "Total Idle Hours": f"{total_idle_hours:.1f}",
                "Total Idle Cost": f"${total_idle_cost:.2f}",
                "Fuel Waste Cost": f"${fuel_waste_cost:.2f}",
                "Operational Cost": f"${operational_cost:.2f}",
                "Number of Idle Events": len(idle_periods),
                "Longest Idle Period": f"{longest_idle:.1f} hours",
                "Average Idle Duration": f"{average_idle:.1f} hours",
                "Cost Impact": "HIGH" if total_idle_cost > 500 else "MEDIUM"
            })

        return cost_analysis