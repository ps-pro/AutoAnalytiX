"""
10-minute Window Synchronization

Extracted from original AutoAnalytiX FUEL_THEFT_DETECTION_MODULE.create_10_minute_synchronized_windows() method.
Creates 10-minute synchronized time windows by averaging sensor readings.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from collections import defaultdict


class TimeSynchronizer:
    """
    Time synchronization functionality extracted from original FUEL_THEFT_DETECTION_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def create_10_minute_synchronized_windows(self, vehicle_id, fuel_data, odometer_data, speed_data):
        """Create 10-minute synchronized time windows by averaging sensor readings"""
        # Combine all timestamps and create 10-minute windows
        all_timestamps = []

        if not fuel_data.empty:
            all_timestamps.extend(fuel_data['TIMESTAMP'].tolist())
        if not odometer_data.empty:
            all_timestamps.extend(odometer_data['TIMESTAMP'].tolist())
        if not speed_data.empty:
            all_timestamps.extend(speed_data['TIMESTAMP'].tolist())

        if not all_timestamps:
            return pd.DataFrame()

        # Sort timestamps and determine time range
        all_timestamps = sorted(set(all_timestamps))
        start_time = min(all_timestamps)
        end_time = max(all_timestamps)

        # Pre-sort all data once for performance
        if not fuel_data.empty:
            fuel_sorted = fuel_data.sort_values('TIMESTAMP').reset_index(drop=True)
        else:
            fuel_sorted = pd.DataFrame()

        if not odometer_data.empty:
            odometer_sorted = odometer_data.sort_values('TIMESTAMP').reset_index(drop=True)
        else:
            odometer_sorted = pd.DataFrame()

        if not speed_data.empty:
            speed_sorted = speed_data.sort_values('TIMESTAMP').reset_index(drop=True)
        else:
            speed_sorted = pd.DataFrame()

        # Create 10-minute windows with optimized filtering
        current_time = start_time
        synchronized_windows = []

        # Use indices to avoid repeated filtering
        fuel_idx = 0
        odometer_idx = 0
        speed_idx = 0

        while current_time < end_time:
            window_start = current_time
            window_end = current_time + timedelta(minutes=10)
            window_center = current_time + timedelta(minutes=5)

            # Collect readings within this 10-minute window
            window_data = {
                'timestamp': window_center,
                'fuel_level': None,
                'odometer': None,
                'speed': None,
                'reading_counts': {'fuel': 0, 'odometer': 0, 'speed': 0}
            }

            # Fuel readings in window using index tracking
            if not fuel_sorted.empty:
                fuel_values = []
                # Advance index to window start
                while fuel_idx < len(fuel_sorted) and fuel_sorted.iloc[fuel_idx]['TIMESTAMP'] < window_start:
                    fuel_idx += 1

                # Collect values in window
                temp_idx = fuel_idx
                while temp_idx < len(fuel_sorted) and fuel_sorted.iloc[temp_idx]['TIMESTAMP'] < window_end:
                    fuel_values.append(fuel_sorted.iloc[temp_idx]['fuel_level'])
                    temp_idx += 1

                if fuel_values:
                    window_data['fuel_level'] = np.mean(fuel_values)
                    window_data['reading_counts']['fuel'] = len(fuel_values)

            # Odometer readings in window using index tracking
            if not odometer_sorted.empty:
                odometer_values = []
                # Advance index to window start
                while odometer_idx < len(odometer_sorted) and odometer_sorted.iloc[odometer_idx]['TIMESTAMP'] < window_start:
                    odometer_idx += 1

                # Collect values in window
                temp_idx = odometer_idx
                while temp_idx < len(odometer_sorted) and odometer_sorted.iloc[temp_idx]['TIMESTAMP'] < window_end:
                    odometer_values.append(odometer_sorted.iloc[temp_idx]['odometer'])
                    temp_idx += 1

                if odometer_values:
                    window_data['odometer'] = np.mean(odometer_values)
                    window_data['reading_counts']['odometer'] = len(odometer_values)

            # Speed readings in window using index tracking
            if not speed_sorted.empty:
                speed_values = []
                # Advance index to window start
                while speed_idx < len(speed_sorted) and speed_sorted.iloc[speed_idx]['TIMESTAMP'] < window_start:
                    speed_idx += 1

                # Collect values in window
                temp_idx = speed_idx
                while temp_idx < len(speed_sorted) and speed_sorted.iloc[temp_idx]['TIMESTAMP'] < window_end:
                    speed_values.append(speed_sorted.iloc[temp_idx]['speed'])
                    temp_idx += 1

                if speed_values:
                    window_data['speed'] = np.mean(speed_values)
                    window_data['reading_counts']['speed'] = len(speed_values)

            # Only include windows with at least fuel and odometer data
            if window_data['fuel_level'] is not None and window_data['odometer'] is not None:
                synchronized_windows.append(window_data)

            current_time = window_end

        # Convert to DataFrame and export
        if synchronized_windows:
            sync_df = pd.DataFrame(synchronized_windows)
            sync_df = sync_df.sort_values('timestamp').reset_index(drop=True)

            self.logger.debug(f"{vehicle_id}: Created {len(sync_df)} synchronized 10-minute windows")
            return sync_df
        else:
            self.logger.warning(f"⚠️  {vehicle_id}: No synchronized windows could be created")
            return pd.DataFrame()