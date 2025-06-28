"""
Module-1_ETL

ETL Pipeline module for AutoAnalytiX.
Handles data loading, transformation, and extraction from multiple telemetry sources.
"""

from .etl_orchestrator import ETL_MODULE

__all__ = ['ETL_MODULE']