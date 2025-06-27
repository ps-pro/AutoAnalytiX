"""
Timestamp Standardization Logic

Extracted from original AutoAnalytiX ETL_MODULE.standardize_timestamps() method.
Handles robust timestamp parsing and standardization across datasets.
"""

import pandas as pd
from dateutil import parser
from tqdm import tqdm


class TimestampProcessor:
    """
    Timestamp standardization functionality extracted from original ETL_MODULE.
    """
    
    def __init__(self, logger):
        self.logger = logger

    def standardize_timestamps(self, df, timestamp_col='timestamp'):
        """Advanced timestamp standardization with robust parsing"""
        df_clean = df.copy()

        def safe_parse_timestamp(ts):
            """Safely parse various timestamp formats"""
            try:
                return parser.parse(str(ts))
            except (ValueError, TypeError):
                return pd.NaT

        # Apply timestamp parsing with progress tracking
        tqdm.pandas(desc=f"Parsing {timestamp_col}")
        df_clean['TIMESTAMP'] = df_clean[timestamp_col].progress_apply(safe_parse_timestamp)

        # Remove invalid timestamps
        initial_count = len(df_clean)
        df_clean = df_clean.dropna(subset=['TIMESTAMP'])
        final_count = len(df_clean)

        # Log timestamp processing statistics
        invalid_timestamps = initial_count - final_count
        if invalid_timestamps > 0:
            self.logger.warning(f"⚠️  Removed {invalid_timestamps:,} invalid timestamps ({invalid_timestamps/initial_count*100:.1f}%)")

        # Remove original timestamp column to avoid confusion
        if timestamp_col in df_clean.columns:
            df_clean.drop(columns=[timestamp_col], inplace=True)

        return df_clean