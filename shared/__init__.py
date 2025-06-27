
"""
AutoAnalytiX Shared Module

This module contains common utilities and helper functions used across all AutoAnalytiX modules.
Provides reusable components for data export, plotting, directory management, 
data validation, and mathematical operations.
"""

__version__ = "1.0.0"
__author__ = "AutoAnalytiX Team"

# Import key classes and functions for easy access
from .data_export import DataExporter
from .plot_utils import PlotManager
from .directory_manager import DirectoryManager
from .data_validation import DataValidator
from .math_utils import MathUtils

__all__ = [
    'DataExporter',
    'PlotManager', 
    'DirectoryManager',
    'DataValidator',
    'MathUtils'
]