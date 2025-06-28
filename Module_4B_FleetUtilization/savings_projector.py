"""
Savings Scenario Projections

Extracted from original AutoAnalytiX FLEET_UTILIZATION_MODULE.calculate_savings_projections() method.
Calculates potential savings from idle reduction scenarios.
"""


class SavingsProjector:
    """
    Savings projection functionality extracted from original FLEET_UTILIZATION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def calculate_savings_projections(self, idle_analysis):
        """Calculate potential savings from idle reduction scenarios"""
        current_annual_cost = idle_analysis['total_idle_cost']

        # Projection scenarios
        scenarios = {
            '25_percent_reduction': {
                'reduction_percentage': 25,
                'annual_savings': current_annual_cost * 0.25,
                'description': "25% Idle Reduction (Basic Training)"
            },
            '50_percent_reduction': {
                'reduction_percentage': 50,
                'annual_savings': current_annual_cost * 0.50,
                'description': "50% Idle Reduction (Comprehensive Program)"
            },
            '75_percent_reduction': {
                'reduction_percentage': 75,
                'annual_savings': current_annual_cost * 0.75,
                'description': "75% Idle Reduction (Advanced Optimization)"
            }
        }

        return scenarios