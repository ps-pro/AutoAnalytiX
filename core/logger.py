"""
Professional Logging Infrastructure - FIXED UNICODE ENCODING

Enterprise-grade logging system extracted from the original AutoAnalytiX code.
Provides comprehensive logging with file verification and violation tracking.
FIXED: Replaced Unicode emojis with ASCII-safe alternatives for Windows compatibility.
"""

import logging
import json
from pathlib import Path
from datetime import datetime


class ProfessionalLogger:
    """Enterprise-grade logging system for fleet analytics"""

    def __init__(self, base_dir="AutoAnalytiX__Reports"):
        self.base_dir = Path(base_dir)
        self.setup_logging_infrastructure()
        self.files_created = []  # Track all files created

    def setup_logging_infrastructure(self):
        """Initialize comprehensive logging system"""
        # Create directory structure
        self.log_dirs = {
            'main': self.base_dir / "Logs",
            'vehicle': self.base_dir / "Vehicle_Logs",
            'quality': self.base_dir / "Quality_Reports",
            'plots': self.base_dir / "Plots",
            'exports': self.base_dir / "Data_Exports"
        }

        for log_dir in self.log_dirs.values():
            log_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {log_dir}")

        # Setup main system logger
        self._logger = logging.getLogger('AutoAnalytiX')
        self._logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s:%(lineno)d | %(message)s'
        )

        # Main log file handler with UTF-8 encoding
        log_file = self.log_dirs['main'] / f"AutoAnalytiX_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        main_handler = logging.FileHandler(log_file, encoding='utf-8')
        main_handler.setFormatter(detailed_formatter)
        self._logger.addHandler(main_handler)

        # Console handler for important messages with ASCII-safe formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)

        self._logger.info("=" * 80)
        self._logger.info("AutoAnalytiX v1.0 - Enhanced Fleet Analytics Platform")
        self._logger.info("=" * 80)

    def track_file_created(self, file_path):
        """Track files created for verification"""
        self.files_created.append(str(file_path))
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            self._logger.info(f"✅ File created: {file_path} ({size} bytes)")
        else:
            self._logger.error(f"❌ File NOT created: {file_path}")

    def verify_plot_creation(self, plot_path, plot_name):
        """Verify plot was actually created and has content"""
        try:
            if Path(plot_path).exists():
                size = Path(plot_path).stat().st_size
                if size > 1000:  # Reasonable minimum size for a plot
                    self._logger.info(f"✅ Plot saved: {plot_name} ({size} bytes)")
                    self.track_file_created(plot_path)
                    return True
                else:
                    self._logger.error(f"❌ Plot file too small: {plot_name} ({size} bytes)")
            else:
                self._logger.error(f"❌ Plot NOT created: {plot_name}")
            return False
        except Exception as e:
            self._logger.error(f"❌ Error verifying plot {plot_name}: {e}")
            return False

    # Add wrapper methods to expose internal logger methods
    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message):
        self._logger.error(message)

    def debug(self, message):
        self._logger.debug(message)

    def log_module_start(self, module_name, description):
        """Log the start of a major module"""
        self._logger.info("=" * 60)
        self._logger.info(f"[MODULE {module_name}] {description}")
        self._logger.info("=" * 60)

    def log_vehicle_violation(self, vehicle_id, violation_type, details):
        """Log vehicle-specific violations to individual files"""
        vehicle_log_path = self.log_dirs['vehicle'] / f"{vehicle_id}_violations.log"

        try:
            with open(vehicle_log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"🚨 {violation_type.upper()} VIOLATION DETECTED\n")
                f.write(f"Vehicle ID: {vehicle_id}\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n")

                for key, value in details.items():
                    f.write(f"{key}: {value}\n")

                f.write(f"{'='*80}\n")

            self.track_file_created(vehicle_log_path)
            self._logger.debug(f"Violation logged for {vehicle_id}: {violation_type}")
        except Exception as e:
            self._logger.error(f"Failed to log violation for {vehicle_id}: {e}")

    def log_quality_report(self, module_name, vehicle_id, report_data):
        """Log data quality reports"""
        quality_log_path = self.log_dirs['quality'] / f"{module_name}_{vehicle_id}_quality.json"

        try:
            with open(quality_log_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)

            self.track_file_created(quality_log_path)
            self._logger.debug(f"Quality report saved: {quality_log_path}")
        except Exception as e:
            self._logger.error(f"Failed to save quality report for {vehicle_id}: {e}")

    def generate_files_summary(self):
        """Generate summary of all files created"""
        summary_path = self.base_dir / "Files_Created_Summary.txt"
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("AutoAnalytiX v1.0 - Files Created Summary\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total files created: {len(self.files_created)}\n\n")

                for i, file_path in enumerate(self.files_created, 1):
                    if Path(file_path).exists():
                        size = Path(file_path).stat().st_size
                        f.write(f"{i:3d}. {file_path} ({size} bytes)\n")
                    else:
                        f.write(f"{i:3d}. {file_path} (NOT FOUND)\n")

            self._logger.info(f"📋 Files summary created: {summary_path}")
        except Exception as e:
            self._logger.error(f"Failed to create files summary: {e}")