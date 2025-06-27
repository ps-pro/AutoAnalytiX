"""
Moving Averages, Statistical Functions

Centralized mathematical utilities used across all AutoAnalytiX modules.
Provides consistent mathematical operations for data analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from scipy import stats
from datetime import datetime, timedelta


class MathUtils:
    """
    Centralized mathematical utility for AutoAnalytiX.
    
    Provides consistent mathematical operations for statistical analysis,
    moving averages, and physics-based calculations.
    """
    
    def __init__(self, logger=None):
        """
        Initialize MathUtils.
        
        Args:
            logger: Logger instance for tracking operations
        """
        self.logger = logger
    
    def calculate_moving_averages(
        self, 
        data_series: pd.Series, 
        windows: List[int] = [5, 10, 20]
    ) -> Dict[str, pd.Series]:
        """
        Calculate multiple moving averages for gradient analysis.
        
        Args:
            data_series: Pandas Series with numeric data
            windows: List of window sizes for moving averages
            
        Returns:
            Dict: Mapping of window name to moving average Series
        """
        moving_averages = {}
        
        for window in windows:
            if len(data_series) >= window:
                ma = data_series.rolling(window=window, center=True).mean()
                moving_averages[f'MA_{window}'] = ma
            else:
                # If insufficient data, create MA with available data
                actual_window = max(1, len(data_series))
                ma = data_series.rolling(window=actual_window, center=True).mean()
                moving_averages[f'MA_{window}'] = ma
        
        return moving_averages
    
    def calculate_acceleration(
        self, 
        speed_values: pd.Series, 
        timestamps: pd.Series,
        time_unit: str = 'minutes'
    ) -> Tuple[pd.Series, Dict[str, Any]]:
        """
        Calculate acceleration from speed and timestamp data.
        
        Args:
            speed_values: Series of speed values
            timestamps: Series of timestamp values
            time_unit: Unit for acceleration ('minutes', 'seconds', 'hours')
            
        Returns:
            Tuple: (acceleration_series, calculation_stats)
        """
        if len(speed_values) != len(timestamps) or len(speed_values) < 2:
            return pd.Series(dtype=float), {'valid_calculations': 0}
        
        # Calculate time differences
        time_diffs = timestamps.diff()
        
        # Convert to specified time unit
        if time_unit == 'minutes':
            time_diffs_numeric = time_diffs.dt.total_seconds() / 60
        elif time_unit == 'seconds':
            time_diffs_numeric = time_diffs.dt.total_seconds()
        elif time_unit == 'hours':
            time_diffs_numeric = time_diffs.dt.total_seconds() / 3600
        else:
            raise ValueError(f"Unsupported time unit: {time_unit}")
        
        # Calculate speed changes
        speed_changes = speed_values.diff().abs()
        
        # Calculate acceleration
        accelerations = speed_changes / time_diffs_numeric
        
        # Filter out infinite and invalid values
        valid_mask = (time_diffs_numeric > 0) & (time_diffs_numeric < 60)  # Reasonable time gaps
        valid_accelerations = accelerations[valid_mask]
        
        stats = {
            'total_calculations': len(accelerations),
            'valid_calculations': len(valid_accelerations),
            'mean_acceleration': valid_accelerations.mean() if len(valid_accelerations) > 0 else 0,
            'max_acceleration': valid_accelerations.max() if len(valid_accelerations) > 0 else 0,
            'time_unit': time_unit
        }
        
        return accelerations, stats
    
    def calculate_mpg(
        self, 
        distance_traveled: float, 
        fuel_consumed_gallons: float
    ) -> Optional[float]:
        """
        Calculate miles per gallon.
        
        Args:
            distance_traveled: Distance in miles
            fuel_consumed_gallons: Fuel consumed in gallons
            
        Returns:
            float: MPG value or None if invalid calculation
        """
        try:
            if fuel_consumed_gallons <= 0:
                return None
            
            mpg = distance_traveled / fuel_consumed_gallons
            
            # Sanity check for reasonable MPG values
            if 0 < mpg < 1000:  # Reasonable range for vehicle MPG
                return mpg
            else:
                return None
                
        except (ZeroDivisionError, TypeError):
            return None
    
    def calculate_fuel_efficiency_ratio(self, calculated_mpg: float, rated_mpg: float) -> float:
        """
        Calculate fuel efficiency ratio for theft detection.
        
        Args:
            calculated_mpg: Calculated MPG from data
            rated_mpg: Rated MPG for the vehicle
            
        Returns:
            float: Efficiency ratio (calculated/rated)
        """
        try:
            if rated_mpg <= 0:
                return 0.0
            
            return calculated_mpg / rated_mpg
            
        except (ZeroDivisionError, TypeError):
            return 0.0
    
    def calculate_percentiles(
        self, 
        data_series: pd.Series, 
        percentiles: List[float] = [25, 50, 75, 90, 95, 99]
    ) -> Dict[str, float]:
        """
        Calculate multiple percentiles for data analysis.
        
        Args:
            data_series: Numeric data series
            percentiles: List of percentile values to calculate
            
        Returns:
            Dict: Mapping of percentile to value
        """
        if data_series.empty:
            return {f'p{p}': 0.0 for p in percentiles}
        
        clean_series = data_series.dropna()
        
        if clean_series.empty:
            return {f'p{p}': 0.0 for p in percentiles}
        
        results = {}
        for p in percentiles:
            results[f'p{p}'] = clean_series.quantile(p / 100)
        
        return results
    
    def calculate_basic_stats(self, data_series: pd.Series) -> Dict[str, float]:
        """
        Calculate basic statistical measures.
        
        Args:
            data_series: Numeric data series
            
        Returns:
            Dict: Basic statistics
        """
        if data_series.empty:
            return {
                'count': 0, 'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0,
                'median': 0.0, 'variance': 0.0, 'skewness': 0.0, 'kurtosis': 0.0
            }
        
        clean_series = data_series.dropna()
        
        if clean_series.empty:
            return {
                'count': 0, 'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0,
                'median': 0.0, 'variance': 0.0, 'skewness': 0.0, 'kurtosis': 0.0
            }
        
        return {
            'count': len(clean_series),
            'mean': clean_series.mean(),
            'std': clean_series.std(),
            'min': clean_series.min(),
            'max': clean_series.max(),
            'median': clean_series.median(),
            'variance': clean_series.var(),
            'skewness': clean_series.skew(),
            'kurtosis': clean_series.kurtosis()
        }
    
    def calculate_time_duration(
        self, 
        start_time: datetime, 
        end_time: datetime,
        unit: str = 'hours'
    ) -> float:
        """
        Calculate duration between two timestamps.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            unit: Unit for duration ('hours', 'minutes', 'days')
            
        Returns:
            float: Duration in specified unit
        """
        try:
            duration = end_time - start_time
            
            if unit == 'hours':
                return duration.total_seconds() / 3600
            elif unit == 'minutes':
                return duration.total_seconds() / 60
            elif unit == 'days':
                return duration.days + (duration.seconds / 86400)
            elif unit == 'seconds':
                return duration.total_seconds()
            else:
                raise ValueError(f"Unsupported time unit: {unit}")
                
        except (TypeError, AttributeError):
            return 0.0
    
    def calculate_idle_cost(
        self, 
        idle_hours: float, 
        cost_per_hour: float = 34.0
    ) -> Dict[str, float]:
        """
        Calculate idle costs using specified formula.
        
        Args:
            idle_hours: Total idle time in hours
            cost_per_hour: Cost per idle hour
            
        Returns:
            Dict: Breakdown of idle costs
        """
        fuel_waste_rate = 4.0  # $4/hour for fuel waste
        operational_rate = 30.0  # $30/hour for operational cost
        
        return {
            'total_idle_hours': idle_hours,
            'fuel_waste_cost': idle_hours * fuel_waste_rate,
            'operational_cost': idle_hours * operational_rate,
            'total_idle_cost': idle_hours * cost_per_hour,
            'cost_per_hour': cost_per_hour
        }
    
    def calculate_utilization_percentage(
        self, 
        active_hours: float, 
        total_hours: float
    ) -> float:
        """
        Calculate utilization percentage.
        
        Args:
            active_hours: Hours of active use
            total_hours: Total hours in period
            
        Returns:
            float: Utilization percentage
        """
        try:
            if total_hours <= 0:
                return 0.0
            
            utilization = (active_hours / total_hours) * 100
            return max(0.0, min(100.0, utilization))  # Clamp to 0-100%
            
        except (ZeroDivisionError, TypeError):
            return 0.0
    
    def detect_threshold_violations(
        self, 
        data_series: pd.Series, 
        thresholds: Dict[str, float]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Detect violations of multiple thresholds.
        
        Args:
            data_series: Data to analyze
            thresholds: Dict of threshold_name -> threshold_value
            
        Returns:
            Dict: Violation analysis for each threshold
        """
        results = {}
        
        if data_series.empty:
            return {name: {'violations': 0, 'percentage': 0.0} for name in thresholds}
        
        clean_series = data_series.dropna()
        total_count = len(clean_series)
        
        for threshold_name, threshold_value in thresholds.items():
            violations = (clean_series > threshold_value).sum()
            percentage = (violations / total_count * 100) if total_count > 0 else 0.0
            
            results[threshold_name] = {
                'threshold_value': threshold_value,
                'violations': violations,
                'percentage': percentage,
                'total_data_points': total_count
            }
        
        return results
    
    def smooth_data(
        self, 
        data_series: pd.Series, 
        method: str = 'rolling',
        window: int = 5
    ) -> pd.Series:
        """
        Smooth data using various methods.
        
        Args:
            data_series: Data to smooth
            method: Smoothing method ('rolling', 'ewm', 'savgol')
            window: Window size for smoothing
            
        Returns:
            pd.Series: Smoothed data
        """
        if data_series.empty:
            return data_series
        
        try:
            if method == 'rolling':
                return data_series.rolling(window=window, center=True).mean()
            elif method == 'ewm':
                return data_series.ewm(span=window).mean()
            elif method == 'savgol':
                from scipy.signal import savgol_filter
                # Ensure odd window size
                if window % 2 == 0:
                    window += 1
                smoothed = savgol_filter(data_series.dropna(), window, polyorder=3)
                return pd.Series(smoothed, index=data_series.dropna().index)
            else:
                raise ValueError(f"Unsupported smoothing method: {method}")
                
        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️  Data smoothing failed: {e}")
            return data_series
    
    def calculate_correlation_matrix(
        self, 
        dataframe: pd.DataFrame, 
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for numeric columns.
        
        Args:
            dataframe: DataFrame with numeric data
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            pd.DataFrame: Correlation matrix
        """
        try:
            # Select only numeric columns
            numeric_cols = dataframe.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                return pd.DataFrame()
            
            return dataframe[numeric_cols].corr(method=method)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Correlation calculation failed: {e}")
            return pd.DataFrame()
    
    def normalize_data(
        self, 
        data_series: pd.Series, 
        method: str = 'minmax'
    ) -> pd.Series:
        """
        Normalize data using various methods.
        
        Args:
            data_series: Data to normalize
            method: Normalization method ('minmax', 'zscore', 'robust')
            
        Returns:
            pd.Series: Normalized data
        """
        if data_series.empty:
            return data_series
        
        clean_series = data_series.dropna()
        
        if clean_series.empty:
            return data_series
        
        try:
            if method == 'minmax':
                min_val = clean_series.min()
                max_val = clean_series.max()
                if max_val == min_val:
                    return pd.Series(0.5, index=data_series.index)
                return (data_series - min_val) / (max_val - min_val)
                
            elif method == 'zscore':
                mean_val = clean_series.mean()
                std_val = clean_series.std()
                if std_val == 0:
                    return pd.Series(0.0, index=data_series.index)
                return (data_series - mean_val) / std_val
                
            elif method == 'robust':
                median_val = clean_series.median()
                mad_val = (clean_series - median_val).abs().median()
                if mad_val == 0:
                    return pd.Series(0.0, index=data_series.index)
                return (data_series - median_val) / mad_val
                
            else:
                raise ValueError(f"Unsupported normalization method: {method}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Data normalization failed: {e}")
            return data_series