"""
Common Validation Functions

Centralized data validation functionality used across all AutoAnalytiX modules.
Provides consistent validation methods for timestamps, numeric data, and ranges.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from dateutil import parser
from typing import Union, Optional, Tuple, List, Any, Dict


class DataValidator:
    """
    Centralized data validation utility for AutoAnalytiX.
    
    Provides consistent validation methods for common data quality checks
    across all modules.
    """
    
    def __init__(self, logger=None):
        """
        Initialize DataValidator.
        
        Args:
            logger: Logger instance for tracking validation operations
        """
        self.logger = logger
        self.validation_stats = {}
    
    def validate_timestamp(self, timestamp_value: Any) -> Optional[datetime]:
        """
        Safely parse and validate timestamp values.
        
        Args:
            timestamp_value: Timestamp value to parse
            
        Returns:
            datetime: Parsed datetime or None if invalid
        """
        try:
            if pd.isna(timestamp_value):
                return None
                
            if isinstance(timestamp_value, datetime):
                return timestamp_value
                
            # Try parsing with dateutil parser
            return parser.parse(str(timestamp_value))
            
        except (ValueError, TypeError):
            return None
    
    def validate_numeric(
        self, 
        value: Any, 
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_zero: bool = True
    ) -> Optional[float]:
        """
        Validate and convert numeric values with range checking.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_zero: Whether zero is allowed
            
        Returns:
            float: Validated numeric value or None if invalid
        """
        try:
            if pd.isna(value):
                return None
                
            # Convert to numeric
            numeric_value = pd.to_numeric(value, errors='coerce')
            
            if pd.isna(numeric_value):
                return None
            
            # Check zero allowance
            if not allow_zero and numeric_value == 0:
                return None
            
            # Check range constraints
            if min_value is not None and numeric_value < min_value:
                return None
                
            if max_value is not None and numeric_value > max_value:
                return None
                
            return float(numeric_value)
            
        except (ValueError, TypeError):
            return None
    
    def validate_fuel_level(self, fuel_value: Any) -> Tuple[Optional[float], str]:
        """
        Validate fuel level values with specific range checking.
        
        Args:
            fuel_value: Fuel level value to validate
            
        Returns:
            Tuple: (validated_value, validation_status)
        """
        validated_value = self.validate_numeric(fuel_value, min_value=0, max_value=100)
        
        if validated_value is None:
            if pd.isna(fuel_value):
                return None, "MISSING"
            else:
                return None, "INVALID_FORMAT"
        
        # Check for range violations
        if validated_value < 0:
            return validated_value, "NEGATIVE_VIOLATION"
        elif validated_value > 100:
            return validated_value, "OVER_100_VIOLATION"
        else:
            return validated_value, "VALID"
    
    def validate_speed(self, speed_value: Any) -> Tuple[Optional[float], str]:
        """
        Validate speed values.
        
        Args:
            speed_value: Speed value to validate
            
        Returns:
            Tuple: (validated_value, validation_status)
        """
        validated_value = self.validate_numeric(speed_value, min_value=0)
        
        if validated_value is None:
            if pd.isna(speed_value):
                return None, "MISSING"
            else:
                return None, "INVALID_FORMAT"
        
        if validated_value < 0:
            return validated_value, "NEGATIVE_SPEED"
        elif validated_value > 200:  # Reasonable upper limit for vehicles
            return validated_value, "EXCESSIVE_SPEED"
        else:
            return validated_value, "VALID"
    
    def validate_odometer(self, odometer_value: Any) -> Tuple[Optional[float], str]:
        """
        Validate odometer values.
        
        Args:
            odometer_value: Odometer value to validate
            
        Returns:
            Tuple: (validated_value, validation_status)
        """
        validated_value = self.validate_numeric(odometer_value, min_value=0)
        
        if validated_value is None:
            if pd.isna(odometer_value):
                return None, "MISSING"
            else:
                return None, "INVALID_FORMAT"
        
        if validated_value == 0:
            return validated_value, "ZERO_READING"
        elif validated_value < 0:
            return validated_value, "NEGATIVE_READING"
        else:
            return validated_value, "VALID"
    
    def validate_dataframe_timestamps(
        self, 
        df: pd.DataFrame, 
        timestamp_col: str = 'timestamp'
    ) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Validate and standardize timestamps in a DataFrame.
        
        Args:
            df: DataFrame to validate
            timestamp_col: Name of timestamp column
            
        Returns:
            Tuple: (cleaned_dataframe, validation_stats)
        """
        if df.empty or timestamp_col not in df.columns:
            return df, {'valid': 0, 'invalid': 0, 'missing': 0}
        
        df_clean = df.copy()
        
        # Validate each timestamp
        valid_timestamps = []
        stats = {'valid': 0, 'invalid': 0, 'missing': 0}
        
        for timestamp_value in df_clean[timestamp_col]:
            validated_ts = self.validate_timestamp(timestamp_value)
            
            if validated_ts is not None:
                valid_timestamps.append(validated_ts)
                stats['valid'] += 1
            else:
                if pd.isna(timestamp_value):
                    stats['missing'] += 1
                else:
                    stats['invalid'] += 1
                valid_timestamps.append(pd.NaT)
        
        # Replace timestamp column with validated values
        df_clean['TIMESTAMP'] = valid_timestamps
        
        # Remove rows with invalid timestamps
        initial_count = len(df_clean)
        df_clean = df_clean.dropna(subset=['TIMESTAMP'])
        final_count = len(df_clean)
        
        # Update stats
        stats['removed'] = initial_count - final_count
        
        # Remove original timestamp column if different name
        if timestamp_col != 'TIMESTAMP' and timestamp_col in df_clean.columns:
            df_clean.drop(columns=[timestamp_col], inplace=True)
        
        if self.logger and stats['invalid'] > 0:
            self.logger.warning(f"⚠️  Timestamp validation: {stats['invalid']} invalid, {stats['removed']} removed")
        
        return df_clean, stats
    
    def validate_numeric_column(
        self, 
        df: pd.DataFrame, 
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_zero: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Validate numeric column in DataFrame.
        
        Args:
            df: DataFrame to validate
            column: Column name to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_zero: Whether zero is allowed
            
        Returns:
            Tuple: (dataframe_with_validated_column, validation_stats)
        """
        if df.empty or column not in df.columns:
            return df, {'valid': 0, 'invalid': 0, 'missing': 0}
        
        df_clean = df.copy()
        stats = {'valid': 0, 'invalid': 0, 'missing': 0, 'out_of_range': 0}
        
        # Validate each value
        validated_values = []
        
        for value in df_clean[column]:
            validated_value = self.validate_numeric(value, min_value, max_value, allow_zero)
            
            if validated_value is not None:
                validated_values.append(validated_value)
                stats['valid'] += 1
            else:
                validated_values.append(np.nan)
                if pd.isna(value):
                    stats['missing'] += 1
                else:
                    # Check if it's out of range vs invalid format
                    try:
                        numeric_val = pd.to_numeric(value, errors='coerce')
                        if not pd.isna(numeric_val):
                            if ((min_value is not None and numeric_val < min_value) or 
                                (max_value is not None and numeric_val > max_value) or
                                (not allow_zero and numeric_val == 0)):
                                stats['out_of_range'] += 1
                            else:
                                stats['invalid'] += 1
                        else:
                            stats['invalid'] += 1
                    except:
                        stats['invalid'] += 1
        
        # Replace column with validated values
        df_clean[column] = validated_values
        
        return df_clean, stats
    
    def check_data_completeness(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Check data completeness for each column.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dict: Column name -> completion percentage
        """
        if df.empty:
            return {}
        
        completeness = {}
        total_rows = len(df)
        
        for column in df.columns:
            non_null_count = df[column].notna().sum()
            completeness[column] = (non_null_count / total_rows) * 100
        
        return completeness
    
    def identify_outliers(
        self, 
        series: pd.Series, 
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> Tuple[pd.Series, Dict[str, Any]]:
        """
        Identify outliers in a numeric series.
        
        Args:
            series: Numeric series to analyze
            method: Outlier detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Tuple: (outlier_mask, outlier_stats)
        """
        if series.empty or not pd.api.types.is_numeric_dtype(series):
            return pd.Series(dtype=bool), {}
        
        clean_series = series.dropna()
        
        if method == 'iqr':
            Q1 = clean_series.quantile(0.25)
            Q3 = clean_series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            outlier_mask = (series < lower_bound) | (series > upper_bound)
            
            stats = {
                'method': 'IQR',
                'threshold': threshold,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'outlier_count': outlier_mask.sum(),
                'outlier_percentage': (outlier_mask.sum() / len(series)) * 100
            }
            
        elif method == 'zscore':
            mean_val = clean_series.mean()
            std_val = clean_series.std()
            
            z_scores = np.abs((series - mean_val) / std_val)
            outlier_mask = z_scores > threshold
            
            stats = {
                'method': 'Z-Score',
                'threshold': threshold,
                'mean': mean_val,
                'std': std_val,
                'outlier_count': outlier_mask.sum(),
                'outlier_percentage': (outlier_mask.sum() / len(series)) * 100
            }
        
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
        
        return outlier_mask, stats
    
    def validate_vehicle_id(self, vehicle_id: Any) -> Optional[str]:
        """
        Validate vehicle ID format.
        
        Args:
            vehicle_id: Vehicle ID to validate
            
        Returns:
            str: Validated vehicle ID or None if invalid
        """
        try:
            if pd.isna(vehicle_id):
                return None
                
            # Convert to string and strip whitespace
            id_str = str(vehicle_id).strip()
            
            # Check if empty after stripping
            if not id_str:
                return None
                
            return id_str
            
        except:
            return None
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of all validation operations performed.
        
        Returns:
            Dict: Summary of validation statistics
        """
        return {
            'validation_stats': self.validation_stats,
            'total_validations': len(self.validation_stats)
        }