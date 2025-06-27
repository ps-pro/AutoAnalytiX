"""
Before/After Quality Reporting

Extracted from original AutoAnalytiX DATAQUALITYASSURANCE_MODULE.generate_quality_report() method.
Generates comprehensive before/after quality report.
"""

import json
from pathlib import Path
from datetime import datetime


class QualityReporter:
    """
    Quality reporting functionality extracted from original DATAQUALITYASSURANCE_MODULE.
    """
    
    def __init__(self, logger, reports_dir):
        self.logger = logger
        self.reports_dir = Path(reports_dir)

    def generate_quality_report(self, vehicle_id, cleaning_stats):
        """Generate comprehensive before/after quality report"""
        report_path = self.reports_dir / "Quality_Reports" / "Before_After" / f"{vehicle_id}_cleaning_report.json"

        try:
            # Calculate overall statistics
            total_initial = sum(stats.get('initial_records', 0) for stats in cleaning_stats.values())
            total_final = sum(stats.get('final_records', 0) for stats in cleaning_stats.values())
            total_removed = total_initial - total_final

            comprehensive_report = {
                'vehicle_id': vehicle_id,
                'cleaning_timestamp': datetime.now().isoformat(),
                'overall_summary': {
                    'total_initial_records': total_initial,
                    'total_final_records': total_final,
                    'total_records_removed': total_removed,
                    'overall_retention_rate': total_final / total_initial * 100 if total_initial > 0 else 0
                },
                'meter_specific_cleaning': cleaning_stats,
                'data_quality_impact': {
                    'significant_cleaning_required': total_removed > (total_initial * 0.05),  # >5% removal
                    'data_reliability_post_cleaning': 'HIGH' if total_final > (total_initial * 0.90) else 'MEDIUM'
                }
            }

            # Save detailed report
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_report, f, indent=2, default=str)

            self.logger.track_file_created(report_path)

            # Log summary statistics
            self.logger.info(f"📊 {vehicle_id} Quality Report:")
            self.logger.info(f"   • Initial records: {total_initial:,}")
            self.logger.info(f"   • Final records: {total_final:,}")
            self.logger.info(f"   • Retention rate: {comprehensive_report['overall_summary']['overall_retention_rate']:.1f}%")

        except Exception as e:
            self.logger.error(f"Failed to generate quality report for {vehicle_id}: {e}")