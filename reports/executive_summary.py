"""
Executive Summary Generation

Extracted from original AutoAnalytiX generate_executive_summary() function.
Generates executive summary combining all business intelligence findings.
"""

from pathlib import Path
from datetime import datetime


def generate_executive_summary(logger, theft_summary, utilization_summary):
    """Generate executive summary combining all business intelligence findings"""

    total_financial_impact = theft_summary['total_estimated_loss'] + utilization_summary['total_idle_cost']

    summary_path = Path("AutoAnalytiX_Reports") / "Executive_Summary.txt"

    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("AUTOANALYTIX - EXECUTIVE BUSINESS INTELLIGENCE SUMMARY\n")
            f.write("="*80 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("FINANCIAL IMPACT SUMMARY:\n")
            f.write("-"*40 + "\n")
            f.write(f"• Total Theft Losses: ${theft_summary['total_estimated_loss']:,.2f}\n")
            f.write(f"• Total Idle Costs: ${utilization_summary['total_idle_cost']:,.2f}\n")
            f.write(f"• TOTAL FINANCIAL IMPACT: ${total_financial_impact:,.2f}\n\n")

            f.write("THEFT DETECTION RESULTS:\n")
            f.write("-"*40 + "\n")
            f.write(f"• Vehicles with theft events: {theft_summary['vehicles_with_theft_events']}\n")
            f.write(f"• Total theft events detected: {theft_summary['total_theft_events']}\n")
            f.write(f"• High priority investigations: {theft_summary['high_priority_events']}\n\n")

            f.write("UTILIZATION ANALYSIS RESULTS:\n")
            f.write("-"*40 + "\n")
            f.write(f"• Fleet average utilization: {utilization_summary['fleet_average_utilization']:.1f}%\n")
            f.write(f"• Total idle hours: {utilization_summary['total_idle_hours']:.1f}\n")
            f.write(f"• Vehicles with excessive idle: {utilization_summary['vehicles_with_excessive_idle']}\n\n")

            f.write("SAVINGS OPPORTUNITIES:\n")
            f.write("-"*40 + "\n")
            f.write(f"• Potential savings (50% idle reduction): ${utilization_summary['potential_savings_50_percent']:,.2f}\n")
            f.write(f"• ROI on optimization programs: {utilization_summary['potential_savings_50_percent']/max(1, utilization_summary['total_idle_cost'])*100:.1f}%\n")

        logger.track_file_created(summary_path)
        logger.info(f"📋 Executive Summary saved: {summary_path}")
        logger.info(f"💰 Total Financial Impact Identified: ${total_financial_impact:,.2f}")

    except Exception as e:
        logger.error(f"Failed to generate executive summary: {e}")