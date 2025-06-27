"""
Utilization Percentage Calculations

Extracted from original AutoAnalytiX FLEET_UTILIZATION_MODULE.calculate_utilization_metrics() method.
Calculates comprehensive utilization metrics.
"""


class UtilizationMetrics:
    """
    Utilization metrics functionality extracted from original FLEET_UTILIZATION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def calculate_utilization_metrics(self, vehicle_id, speed_data, idle_analysis):
        """Calculate comprehensive utilization metrics"""
        if speed_data.empty:
            return {}

        # Calculate total operating time
        speed_sorted = speed_data.sort_values('TIMESTAMP')
        total_time_span = (speed_sorted['TIMESTAMP'].max() - speed_sorted['TIMESTAMP'].min()).total_seconds() / 3600  # hours

        # Calculate active vs idle time
        total_idle_hours = idle_analysis['total_idle_hours']
        active_hours = total_time_span - total_idle_hours

        # Calculate utilization percentage
        utilization_percentage = (active_hours / total_time_span * 100) if total_time_span > 0 else 0
        idle_percentage = (total_idle_hours / total_time_span * 100) if total_time_span > 0 else 0

        # Calculate efficiency scores
        efficiency_score = max(0, min(100, utilization_percentage))  # 0-100 scale

        if efficiency_score >= 85:
            efficiency_grade = "EXCELLENT"
        elif efficiency_score >= 70:
            efficiency_grade = "GOOD"
        elif efficiency_score >= 55:
            efficiency_grade = "FAIR"
        else:
            efficiency_grade = "POOR"

        utilization_metrics = {
            'total_time_span_hours': total_time_span,
            'active_hours': active_hours,
            'idle_hours': total_idle_hours,
            'utilization_percentage': utilization_percentage,
            'idle_percentage': idle_percentage,
            'efficiency_score': efficiency_score,
            'efficiency_grade': efficiency_grade,
            'data_span_days': total_time_span / 24
        }

        return utilization_metrics