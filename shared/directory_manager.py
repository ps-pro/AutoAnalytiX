"""
Directory Setup and File Tracking

Centralized directory management and file tracking functionality
used across all AutoAnalytiX modules.
"""

import os
from pathlib import Path
from typing import Dict, List, Union, Optional
from datetime import datetime


class DirectoryManager:
    """
    Centralized directory management utility for AutoAnalytiX.
    
    Handles directory creation, file tracking, and output organization
    across all modules.
    """
    
    def __init__(self, base_dir: str = "AutoAnalytiX__Reports", logger=None):
        """
        Initialize DirectoryManager.
        
        Args:
            base_dir: Base directory name for all outputs
            logger: Logger instance for tracking operations
        """
        self.base_dir = Path(base_dir)
        self.logger = logger
        self.files_created = []
        self.directories_created = []
        
    def setup_base_structure(self) -> Dict[str, Path]:
        """
        Setup base directory structure for AutoAnalytiX.
        
        Returns:
            Dict: Mapping of directory names to Path objects
        """
        base_directories = {
            'main': self.base_dir,
            'logs': self.base_dir / "Logs",
            'vehicle_logs': self.base_dir / "Vehicle_Logs", 
            'quality_reports': self.base_dir / "Quality_Reports",
            'plots': self.base_dir / "Plots",
            'data_exports': self.base_dir / "Data_Exports"
        }
        
        created_dirs = {}
        for name, dir_path in base_directories.items():
            if self.create_directory(dir_path):
                created_dirs[name] = dir_path
                
        return created_dirs
    
    def setup_quality_inspection_directories(self) -> Dict[str, Path]:
        """
        Setup directory structure for Data Quality Inspection module.
        
        Returns:
            Dict: Mapping of directory names to Path objects
        """
        quality_directories = {
            'speed_quality': self.base_dir / "Plots" / "Speed_Quality",
            'odometer_quality': self.base_dir / "Plots" / "Odometer_Quality", 
            'fuel_quality': self.base_dir / "Plots" / "Fuel_Quality"
        }
        
        created_dirs = {}
        for name, dir_path in quality_directories.items():
            if self.create_directory(dir_path):
                created_dirs[name] = dir_path
                
        return created_dirs
    
    def setup_quality_assurance_directories(self) -> Dict[str, Path]:
        """
        Setup directory structure for Data Quality Assurance module.
        
        Returns:
            Dict: Mapping of directory names to Path objects
        """
        assurance_directories = {
            'before_after': self.base_dir / "Quality_Reports" / "Before_After",
            'cleaned_exports': self.base_dir / "Cleaned_Data_Exports"
        }
        
        created_dirs = {}
        for name, dir_path in assurance_directories.items():
            if self.create_directory(dir_path):
                created_dirs[name] = dir_path
                
        return created_dirs
    
    def setup_theft_detection_directories(self) -> Dict[str, Path]:
        """
        Setup directory structure for Fuel Theft Detection module.
        
        Returns:
            Dict: Mapping of directory names to Path objects
        """
        theft_directories = {
            'theft_detection': self.base_dir / "Theft_Detection",
            'synchronized_data': self.base_dir / "Synchronized_Data",
            'theft_plots': self.base_dir / "Plots" / "Theft_Analysis"
        }
        
        created_dirs = {}
        for name, dir_path in theft_directories.items():
            if self.create_directory(dir_path):
                created_dirs[name] = dir_path
                
        return created_dirs
    
    def setup_utilization_directories(self) -> Dict[str, Path]:
        """
        Setup directory structure for Fleet Utilization module.
        
        Returns:
            Dict: Mapping of directory names to Path objects
        """
        utilization_directories = {
            'utilization_analysis': self.base_dir / "Utilization_Analysis",
            'utilization_plots': self.base_dir / "Plots" / "Utilization"
        }
        
        created_dirs = {}
        for name, dir_path in utilization_directories.items():
            if self.create_directory(dir_path):
                created_dirs[name] = dir_path
                
        return created_dirs
    
    def create_directory(self, dir_path: Union[str, Path]) -> bool:
        """
        Create directory with error handling.
        
        Args:
            dir_path: Path to directory to create
            
        Returns:
            bool: True if directory created successfully
        """
        try:
            dir_path = Path(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Track directory creation
            if str(dir_path) not in self.directories_created:
                self.directories_created.append(str(dir_path))
                
                if self.logger:
                    self.logger.info(f"[OK] Created directory: {dir_path}")
                    
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Failed to create directory {dir_path}: {e}")
            return False
    
    def track_file_created(self, file_path: Union[str, Path], description: str = None):
        """
        Track files created for verification and summary reporting.
        
        Args:
            file_path: Path to file that was created
            description: Optional description of the file
        """
        file_path = Path(file_path)
        
        file_info = {
            'file_path': str(file_path),
            'description': description or file_path.name,
            'timestamp': datetime.now(),
            'exists': file_path.exists(),
            'size_bytes': file_path.stat().st_size if file_path.exists() else 0
        }
        
        self.files_created.append(file_info)
        
        if self.logger:
            if file_path.exists():
                size = file_path.stat().st_size
                self.logger.info(f"[OK] File created: {file_path} ({size} bytes)")
            else:
                self.logger.error(f"[ERROR] File NOT created: {file_path}")
    
    def verify_file_exists(self, file_path: Union[str, Path]) -> bool:
        """
        Verify that a file exists and has content.
        
        Args:
            file_path: Path to file to verify
            
        Returns:
            bool: True if file exists and has content
        """
        try:
            file_path = Path(file_path)
            
            if file_path.exists():
                size = file_path.stat().st_size
                return size > 0
            else:
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Error verifying file {file_path}: {e}")
            return False
    
    def get_files_summary(self) -> Dict[str, any]:
        """
        Get summary of all files created.
        
        Returns:
            Dict: Summary statistics of files created
        """
        existing_files = [f for f in self.files_created if f['exists']]
        total_size = sum(f['size_bytes'] for f in existing_files)
        
        return {
            'total_files_tracked': len(self.files_created),
            'existing_files': len(existing_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files': self.files_created
        }
    
    def generate_files_summary_report(self, output_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Generate comprehensive files summary report.
        
        Args:
            output_path: Optional custom path for summary file
            
        Returns:
            bool: True if summary generated successfully
        """
        try:
            if output_path is None:
                output_path = self.base_dir / "Files_Created_Summary.txt"
            else:
                output_path = Path(output_path)
            
            summary = self.get_files_summary()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("AutoAnalytiX Files Created Summary\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total files tracked: {summary['total_files_tracked']}\n")
                f.write(f"Existing files: {summary['existing_files']}\n")
                f.write(f"Total size: {summary['total_size_mb']} MB\n\n")
                
                f.write("File Details:\n")
                f.write("-" * 30 + "\n")
                
                for i, file_info in enumerate(summary['files'], 1):
                    status = "EXISTS" if file_info['exists'] else "MISSING"
                    size_mb = round(file_info['size_bytes'] / (1024 * 1024), 3)
                    
                    f.write(f"{i:3d}. {file_info['file_path']}\n")
                    f.write(f"     Status: {status} | Size: {size_mb} MB\n")
                    f.write(f"     Description: {file_info['description']}\n")
                    f.write(f"     Created: {file_info['timestamp']}\n\n")
            
            # Track the summary file itself
            self.track_file_created(output_path, "Files Summary Report")
            
            if self.logger:
                self.logger.info(f"📄 Files summary report created: {output_path}")
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Failed to generate files summary: {e}")
            return False
    
    def cleanup_empty_directories(self) -> int:
        """
        Remove empty directories from the base directory structure.
        
        Returns:
            int: Number of directories removed
        """
        removed_count = 0
        
        try:
            # Walk through all directories in base_dir
            for dir_path in sorted(self.base_dir.rglob('*'), reverse=True):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    try:
                        dir_path.rmdir()
                        removed_count += 1
                        if self.logger:
                            self.logger.info(f"🗑️  Removed empty directory: {dir_path}")
                    except OSError:
                        pass  # Directory not empty or permission issue
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Error during directory cleanup: {e}")
        
        return removed_count
    
    def get_directory_structure(self) -> Dict[str, any]:
        """
        Get current directory structure under base_dir.
        
        Returns:
            Dict: Directory structure information
        """
        structure = {
            'base_directory': str(self.base_dir),
            'exists': self.base_dir.exists(),
            'directories': [],
            'total_directories': 0,
            'total_files': 0
        }
        
        try:
            if self.base_dir.exists():
                for item in self.base_dir.rglob('*'):
                    if item.is_dir():
                        structure['directories'].append(str(item.relative_to(self.base_dir)))
                        structure['total_directories'] += 1
                    else:
                        structure['total_files'] += 1
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Error analyzing directory structure: {e}")
        
        return structure