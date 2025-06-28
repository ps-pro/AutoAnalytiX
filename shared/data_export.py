"""
Data Export Functionality

Centralized CSV export functionality used across all AutoAnalytiX modules.
Provides consistent export methods with error handling and file tracking.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime


class DataExporter:
    """
    Centralized data export utility for AutoAnalytiX.
    
    Handles CSV exports, JSON exports, and file tracking across all modules.
    """
    
    def __init__(self, logger=None):
        """
        Initialize DataExporter.
        
        Args:
            logger: Logger instance for tracking exports
        """
        self.logger = logger
        self.exports_completed = []
    
    def export_to_csv(
        self, 
        data: pd.DataFrame, 
        file_path: Union[str, Path], 
        description: str = None
    ) -> bool:
        """
        Export DataFrame to CSV with error handling.
        
        Args:
            data: DataFrame to export
            file_path: Path where CSV should be saved
            description: Optional description for logging
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export DataFrame
            data.to_csv(file_path, index=False)
            
            # Track export
            self._track_export(file_path, description or "CSV Export")
            
            # Log success
            if self.logger:
                size = file_path.stat().st_size
                self.logger.info(f"[OK] CSV Export: {file_path} ({size} bytes)")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] CSV Export failed: {file_path} - {e}")
            return False
    
    def export_to_json(
        self, 
        data: Dict[str, Any], 
        file_path: Union[str, Path], 
        description: str = None
    ) -> bool:
        """
        Export dictionary to JSON with error handling.
        
        Args:
            data: Dictionary to export
            file_path: Path where JSON should be saved  
            description: Optional description for logging
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export JSON with proper serialization
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Track export
            self._track_export(file_path, description or "JSON Export")
            
            # Log success
            if self.logger:
                size = file_path.stat().st_size
                self.logger.info(f"[OK] JSON Export: {file_path} ({size} bytes)")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] JSON Export failed: {file_path} - {e}")
            return False
    
    def export_raw_data_summary(
        self, 
        datasets: Dict[str, pd.DataFrame], 
        export_dir: Union[str, Path]
    ) -> bool:
        """
        Export raw data summary for ETL module.
        
        Args:
            datasets: Dictionary of dataset name -> DataFrame
            export_dir: Directory for export
            
        Returns:
            bool: True if export successful
        """
        try:
            export_dir = Path(export_dir)
            
            summary = {}
            for name, df in datasets.items():
                summary[name] = {
                    'records': len(df),
                    'columns': df.columns.tolist(),
                    'date_range': self._get_date_range(df) if 'timestamp' in df.columns else 'N/A'
                }
            
            summary_path = export_dir / "raw_data_summary.json"
            return self.export_to_json(summary, summary_path, "Raw Data Summary")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Raw data summary export failed: {e}")
            return False
    
    def export_cleaned_data(
        self, 
        vehicle_id: str, 
        cleaned_vehicle_data: Dict[str, pd.DataFrame], 
        export_dir: Union[str, Path]
    ) -> bool:
        """
        Export cleaned data for Quality Assurance module.
        
        Args:
            vehicle_id: Vehicle identifier
            cleaned_vehicle_data: Dictionary of meter type -> cleaned DataFrame  
            export_dir: Directory for export
            
        Returns:
            bool: True if all exports successful
        """
        try:
            export_dir = Path(export_dir)
            all_successful = True
            
            for meter_type, meter_data in cleaned_vehicle_data.items():
                if not meter_data.empty:
                    csv_path = export_dir / f"{vehicle_id}_{meter_type}_cleaned.csv"
                    success = self.export_to_csv(
                        meter_data, 
                        csv_path, 
                        f"{vehicle_id} {meter_type} Cleaned Data"
                    )
                    all_successful = all_successful and success
            
            return all_successful
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Cleaned data export failed for {vehicle_id}: {e}")
            return False
    
    def export_synchronized_data(
        self, 
        vehicle_id: str, 
        sync_data: pd.DataFrame, 
        export_dir: Union[str, Path]
    ) -> bool:
        """
        Export synchronized data for Fuel Theft Detection module.
        
        Args:
            vehicle_id: Vehicle identifier
            sync_data: Synchronized data DataFrame
            export_dir: Directory for export
            
        Returns:
            bool: True if export successful
        """
        try:
            export_dir = Path(export_dir)
            export_path = export_dir / f"{vehicle_id}_synchronized_10min.csv"
            
            return self.export_to_csv(
                sync_data, 
                export_path, 
                f"{vehicle_id} Synchronized Data"
            )
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Synchronized data export failed for {vehicle_id}: {e}")
            return False
    
    def export_theft_events(
        self, 
        vehicle_id: str, 
        theft_events: list, 
        export_dir: Union[str, Path]
    ) -> bool:
        """
        Export theft events for Fuel Theft Detection module.
        
        Args:
            vehicle_id: Vehicle identifier
            theft_events: List of theft event dictionaries
            export_dir: Directory for export
            
        Returns:
            bool: True if export successful
        """
        try:
            if not theft_events:
                return True  # No events to export
                
            export_dir = Path(export_dir)
            df = pd.DataFrame(theft_events)
            export_path = export_dir / f"{vehicle_id}_theft_events.csv"
            
            return self.export_to_csv(
                df, 
                export_path, 
                f"{vehicle_id} Theft Events"
            )
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Theft events export failed for {vehicle_id}: {e}")
            return False
    
    def export_utilization_data(
        self, 
        vehicle_id: str, 
        idle_analysis: Dict[str, Any], 
        utilization_metrics: Dict[str, Any], 
        export_dir: Union[str, Path]
    ) -> bool:
        """
        Export utilization analysis for Fleet Utilization module.
        
        Args:
            vehicle_id: Vehicle identifier
            idle_analysis: Idle analysis results
            utilization_metrics: Utilization metrics
            export_dir: Directory for export
            
        Returns:
            bool: True if all exports successful
        """
        try:
            export_dir = Path(export_dir)
            all_successful = True
            
            # Export idle periods if available
            if idle_analysis.get('idle_periods'):
                idle_df = pd.DataFrame(idle_analysis['idle_periods'])
                idle_path = export_dir / f"{vehicle_id}_idle_periods.csv"
                success = self.export_to_csv(
                    idle_df, 
                    idle_path, 
                    f"{vehicle_id} Idle Periods"
                )
                all_successful = all_successful and success
            
            # Export utilization summary
            summary_data = {
                'vehicle_id': [vehicle_id],
                'total_idle_hours': [idle_analysis.get('total_idle_hours', 0)],
                'total_idle_cost': [idle_analysis.get('total_idle_cost', 0)],
                'utilization_percentage': [utilization_metrics.get('utilization_percentage', 0)],
                'efficiency_grade': [utilization_metrics.get('efficiency_grade', 'N/A')]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_path = export_dir / f"{vehicle_id}_utilization_summary.csv"
            success = self.export_to_csv(
                summary_df, 
                summary_path, 
                f"{vehicle_id} Utilization Summary"
            )
            all_successful = all_successful and success
            
            return all_successful
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Utilization data export failed for {vehicle_id}: {e}")
            return False
    
    def _track_export(self, file_path: Path, description: str):
        """Track completed exports for summary reporting."""
        self.exports_completed.append({
            'file_path': str(file_path),
            'description': description,
            'timestamp': datetime.now(),
            'size_bytes': file_path.stat().st_size if file_path.exists() else 0
        })
    
    def _get_date_range(self, df: pd.DataFrame) -> Dict[str, str]:
        """Extract date range from DataFrame with timestamp column."""
        try:
            timestamp_col = 'timestamp' if 'timestamp' in df.columns else 'TIMESTAMP'
            if timestamp_col in df.columns:
                return {
                    'start': str(df[timestamp_col].min()),
                    'end': str(df[timestamp_col].max())
                }
        except Exception:
            pass
        return {'start': 'N/A', 'end': 'N/A'}
    
    def generate_export_summary(self, output_path: Union[str, Path]) -> bool:
        """
        Generate summary of all exports completed.
        
        Args:
            output_path: Path for export summary file
            
        Returns:
            bool: True if summary generated successfully
        """
        try:
            summary = {
                'total_exports': len(self.exports_completed),
                'exports': self.exports_completed,
                'summary_generated': str(datetime.now())
            }
            
            return self.export_to_json(summary, output_path, "Export Summary")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Export summary generation failed: {e}")
            return False