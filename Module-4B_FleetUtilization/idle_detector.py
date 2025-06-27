"""
Idle Period Identification (>5 min)

Extracted from original AutoAnalytiX FLEET_UTILIZATION_MODULE.identify_idle_periods() method.
Identifies idle periods: speed = 0 for >5 consecutive minutes.
"""


class IdleDetector:
    """
    Idle detection functionality extracted from original FLEET_UTILIZATION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def identify_idle_periods(self, vehicle_id, speed_data):
        """Identify idle periods: speed = 0 for >5 consecutive minutes"""
        if speed_data.empty:
            return []

        speed_sorted = speed_data.sort_values('TIMESTAMP').copy()
        speed_sorted['is_idle'] = speed_sorted['speed'] == 0

        idle_periods = []
        current_idle_start = None

        for idx, row in speed_sorted.iterrows():
            if row['is_idle']:
                if current_idle_start is None:
                    current_idle_start = row['TIMESTAMP']
            else:
                if current_idle_start is not None:
                    idle_duration = (row['TIMESTAMP'] - current_idle_start).total_seconds() / 60  # minutes

                    # Only record idle periods >5 minutes as specified
                    if idle_duration > 5:
                        idle_periods.append({
                            'start_time': current_idle_start,
                            'end_time': row['TIMESTAMP'],
                            'duration_minutes': idle_duration,
                            'duration_hours': idle_duration / 60
                        })

                    current_idle_start = None

        # Handle case where data ends during idle period
        if current_idle_start is not None:
            last_timestamp = speed_sorted['TIMESTAMP'].iloc[-1]
            idle_duration = (last_timestamp - current_idle_start).total_seconds() / 60

            if idle_duration > 5:
                idle_periods.append({
                    'start_time': current_idle_start,
                    'end_time': last_timestamp,
                    'duration_minutes': idle_duration,
                    'duration_hours': idle_duration / 60
                })

        return idle_periods