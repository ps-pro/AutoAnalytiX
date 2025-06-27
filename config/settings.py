"""
Project-wide Settings and Configuration

Configuration settings extracted from the original AutoAnalytiX code.
Contains plotting parameters, cost calculations, thresholds, and analysis settings.
"""

# =============================================================================
# PLOTTING CONFIGURATION
# =============================================================================

PLOT_CONFIG = {
    # High-quality plotting configuration from original code
    'figure_size': (16, 12),
    'figure_dpi': 150,
    'savefig_dpi': 300,
    'savefig_bbox': 'tight',
    'font_size': 12,
    'axes_titlesize': 16,
    'axes_labelsize': 14,
    'legend_fontsize': 12,
    'style': 'seaborn-v0_8',
    'palette': 'husl',
    'grid_alpha': 0.3,
    'minimum_plot_size_bytes': 1000  # For plot verification
}

# =============================================================================
# COST CONFIGURATION  
# =============================================================================

COST_CONFIG = {
    # Idle cost calculations from original code
    'idle_cost_per_hour': 34.00,  # Total idle cost per hour
    'fuel_waste_rate': 4.00,      # $4/hour for fuel waste
    'operational_rate': 30.00,    # $30/hour for operational cost
    'fuel_price_per_gallon': 5.00  # For theft value estimation
}

# =============================================================================
# THRESHOLD CONFIGURATION
# =============================================================================

THRESHOLD_CONFIG = {
    # Speed acceleration thresholds from original code
    'acceleration_thresholds': [10, 20, 30, 40, 50, 75, 100],  # mph/min
    'severe_acceleration_threshold': 50,  # mph/min for violation logging
    'critical_threshold_30': 30,  # Critical acceleration threshold
    
    # Fuel analysis thresholds
    'fuel_large_drop_threshold': -20,  # More than 20% drop
    'fuel_min_range': 0,    # Minimum valid fuel level
    'fuel_max_range': 100,  # Maximum valid fuel level
    
    # Odometer analysis thresholds  
    'odometer_large_decrease': -50,  # Large decrease threshold (miles)
    
    # Speed validation thresholds
    'max_reasonable_speed': 200,  # mph - reasonable upper limit
    
    # Time gap thresholds for acceleration calculation
    'min_time_gap_minutes': 0,
    'max_time_gap_minutes': 60,
    
    # Idle detection threshold
    'minimum_idle_duration_minutes': 5,  # >5 minutes for idle period
    
    # MPG validation thresholds
    'mpg_sensor_error_threshold': 50,   # Above this = sensor error
    'mpg_theft_investigation_threshold': 2,  # Below this = investigate theft
    'max_reasonable_mpg': 1000  # Upper bound for MPG validation
}

# =============================================================================
# DIRECTORY CONFIGURATION
# =============================================================================

DIRECTORY_CONFIG = {
    # Base directory name from original code
    'base_directory': "AutoAnalytiX__Reports",
    
    # Subdirectory names
    'logs_dir': "Logs",
    'vehicle_logs_dir': "Vehicle_Logs", 
    'quality_reports_dir': "Quality_Reports",
    'plots_dir': "Plots",
    'data_exports_dir': "Data_Exports",
    'cleaned_data_exports_dir': "Cleaned_Data_Exports",
    'theft_detection_dir': "Theft_Detection",
    'synchronized_data_dir': "Synchronized_Data",
    'utilization_analysis_dir': "Utilization_Analysis",
    
    # Plot subdirectories
    'speed_quality_dir': "Speed_Quality",
    'odometer_quality_dir': "Odometer_Quality",
    'fuel_quality_dir': "Fuel_Quality", 
    'theft_analysis_dir': "Theft_Analysis",
    'utilization_plots_dir': "Utilization",
    'before_after_dir': "Before_After"
}

# =============================================================================
# ANALYSIS CONFIGURATION
# =============================================================================

ANALYSIS_CONFIG = {
    # Moving average windows from original code
    'moving_average_windows': [5, 10, 20],
    
    # Synchronization settings
    'synchronization_window_minutes': 10,  # 10-minute windows
    
    # Efficiency ratio thresholds for theft detection
    'efficiency_ratio_critical': 0.3,   # Below this = CRITICAL
    'efficiency_ratio_high': 0.5,       # Below this = HIGH  
    'efficiency_ratio_medium': 0.7,     # Below this = MEDIUM
    
    # Data quality scoring
    'minimum_data_quality_percentage': 90,  # For high reliability rating
    'significant_cleaning_threshold': 0.05,  # >5% removal = significant
    
    # Utilization grading thresholds
    'utilization_excellent': 85,  # >= 85% = EXCELLENT
    'utilization_good': 70,       # >= 70% = GOOD
    'utilization_fair': 55,       # >= 55% = FAIR
    # Below 55% = POOR
    
    # Cost impact thresholds
    'high_idle_cost_threshold': 500,    # Above this = HIGH impact
    'medium_idle_cost_threshold': 100,  # Above this = MEDIUM impact
    'significant_cost_threshold': 50,   # Log if above this
    
    # Violation count thresholds
    'excessive_idle_vehicle_threshold': 10,  # >10 events = excessive
    'high_priority_violation_threshold': 10  # >10 violations = high priority
}

# =============================================================================
# FILE NAMING PATTERNS
# =============================================================================

FILE_PATTERNS = {
    'log_file_pattern': "AutoAnalytiX_{timestamp}.log",
    'violation_file_pattern': "{vehicle_id}_violations.log",
    'quality_report_pattern': "{module_name}_{vehicle_id}_quality.json",
    'cleaned_data_pattern': "{vehicle_id}_{meter_type}_cleaned.csv",
    'synchronized_data_pattern': "{vehicle_id}_synchronized_10min.csv",
    'theft_events_pattern': "{vehicle_id}_theft_events.csv",
    'idle_periods_pattern': "{vehicle_id}_idle_periods.csv",
    'utilization_summary_pattern': "{vehicle_id}_utilization_summary.csv",
    'plot_pattern': "{vehicle_id}_{analysis_type}_analysis.pdf"
}