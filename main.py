"""
Main Entry Point for AutoAnalytiX Application

Extracted from original AutoAnalytiX main() function.
Orchestrates the complete AutoAnalytiX pipeline.
"""

# Set matplotlib backend FIRST
import matplotlib
matplotlib.use('Agg')

# Core imports
import sys
from pathlib import Path

# Add module directories to Python path
sys.path.insert(0, str(Path("Module-1_ETL")))
sys.path.insert(0, str(Path("Module-2_DataQualityInspection")))
sys.path.insert(0, str(Path("Module-3_DataQualityAssurance")))
sys.path.insert(0, str(Path("Module-4A_FuelTheftDetection")))
sys.path.insert(0, str(Path("Module-4B_FleetUtilization")))

# Import core modules
from core.logger import ProfessionalLogger
from reports.executive_summary import generate_executive_summary

# Import module orchestrators
from etl_orchestrator import ETL_MODULE
from quality_orchestrator import DATAQUALITYINSPECTION_MODULE
from cleaning_orchestrator import DATAQUALITYASSURANCE_MODULE
from theft_orchestrator import FUEL_THEFT_DETECTION_MODULE
from utilization_orchestrator import FLEET_UTILIZATION_MODULE


def main():
    """Main execution framework for AutoAnalytiX .0"""

    # Initialize professional logging system
    logger = ProfessionalLogger()

    try:
        # MODULE 1: ETL Pipeline
        etl_processor = ETL_MODULE(logger)

        # Local environment data path
        data_path = "data/"

        # Execute ETL pipeline
        etl_results = etl_processor.execute_etl_pipeline(data_path)

        # MODULE 2: Data Quality Inspection
        quality_inspector = DATAQUALITYINSPECTION_MODULE(
            etl_results['vehicle_meter_data'],
            etl_results['vehicle_metadata'],
            logger
        )

        quality_issues = quality_inspector.execute_quality_inspection()

        # MODULE 3: Data Quality Assurance
        data_cleaner = DATAQUALITYASSURANCE_MODULE(
            etl_results['vehicle_meter_data'],
            quality_issues,
            logger
        )

        cleaned_data = data_cleaner.execute_data_cleaning()

        # MODULE 4A: Fuel Theft Detection
        theft_detector = FUEL_THEFT_DETECTION_MODULE(
            cleaned_data,
            etl_results['vehicle_metadata'],
            logger
        )

        theft_events, theft_summary = theft_detector.execute_theft_detection()

        # MODULE 4B: Fleet Utilization Analysis
        utilization_analyzer = FLEET_UTILIZATION_MODULE(
            cleaned_data,
            logger
        )

        utilization_analysis, utilization_summary = utilization_analyzer.execute_utilization_analysis()

        # Generate Executive Summary
        generate_executive_summary(logger, theft_summary, utilization_summary)

        # Generate summary of all files created
        logger.generate_files_summary()

        logger.info(f"📄 TOTAL FILES CREATED: {len(logger.files_created)}")

        logger.info("🎉 AutoAnalytiX - ALL MODULES COMPLETED SUCCESSFULLY!")
        logger.info("📁 Comprehensive reports saved to AutoAnalytiX__Reports directory")

        return {
            'cleaned_data': cleaned_data,
            'theft_events': theft_events,
            'theft_summary': theft_summary,
            'utilization_analysis': utilization_analysis,
            'utilization_summary': utilization_summary
        }

    except Exception as e:
        logger.error(f"Execution failed: {e}")
        raise


if __name__ == "__main__":
    results = main()