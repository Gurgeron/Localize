#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reporter Module

This module is responsible for generating reports based on the localization testing results.
It creates CSV reports, summary reports, and optionally can generate HTML or JSON reports.
"""

import os
import csv
import json
import logging
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil

# Import our modules
from .config_loader import Config

# Setup logging
logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Class for generating reports based on localization testing results
    """
    
    def __init__(self, session_dir: Path = None):
        """Initialize the ReportGenerator"""
        self.config = Config()
        self.reports_dir = Path(self.config.get('output.reports_dir', './reports'))
        self.session_dir = session_dir
        
        # Ensure reports directory exists
        if not self.reports_dir.exists():
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            
    def generate_report(self, missing_translations: Dict[str, Any], 
                        filename: Optional[str] = None) -> Optional[str]:
        """
        Generate a CSV report of missing translations
        
        Args:
            missing_translations (Dict[str, Any]): Dictionary of missing translations by page and section
            filename (Optional[str]): Optional filename for the report
            
        Returns:
            Optional[str]: Path to the generated report, or None if generation failed
        """
        try:
            # Create filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"localization_report_{timestamp}.csv"
                
            # Create full path
            report_path = self.reports_dir / filename
            
            # CSV headers
            headers = ["Page", "Section", "Text", "Language", "Confidence", "Issue Type"]
            
            # Open CSV file for writing
            with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                # Write data for each page and section
                for page_name, sections in missing_translations.items():
                    for section_name, items in sections.items():
                        for item in items:
                            writer.writerow([
                                page_name,
                                section_name,
                                item["text"],
                                item.get("language", "unknown"),
                                item.get("confidence", ""),
                                item.get("issue_type", "Missing Translation")
                            ])
            
            logger.info(f"CSV report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            return None
            
    def generate_summary_report(self, missing_translations: Dict[str, Any],
                              filename: Optional[str] = None) -> Optional[str]:
        """
        Generate a summary CSV report with counts by page
        
        Args:
            missing_translations (Dict[str, Any]): Dictionary of missing translations by page and section
            filename (Optional[str]): Optional filename for the report
            
        Returns:
            Optional[str]: Path to the generated report, or None if generation failed
        """
        try:
            # Create filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"localization_report_summary_{timestamp}.csv"
                
            # Create full path
            report_path = self.reports_dir / filename
            
            # Calculate summary data
            summary_data = []
            
            for page_name, sections in missing_translations.items():
                page_total = 0
                section_counts = {}
                
                for section_name, items in sections.items():
                    # Skip if items is not a list or is empty
                    if not isinstance(items, list) or not items:
                        continue
                        
                    count = len(items)
                    section_counts[section_name] = count
                    page_total += count
                    
                summary_data.append({
                    "page_name": page_name,
                    "total_issues": page_total,
                    "sections": section_counts
                })
                
            # Sort by most issues first
            summary_data.sort(key=lambda x: x["total_issues"], reverse=True)
            
            # CSV headers
            headers = ["Page", "Total Issues", "Main Page Issues", "Modal Issues", "Details"]
            
            # Open CSV file for writing
            with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                # Write data for each page
                for page_data in summary_data:
                    main_issues = page_data["sections"].get("main", 0)
                    modal_issues = sum(count for section, count in page_data["sections"].items() if section != "main")
                    
                    # Create details string
                    details = []
                    for section, count in page_data["sections"].items():
                        if section == "main":
                            continue  # Skip main as it's in its own column
                        details.append(f"{section}: {count}")
                        
                    writer.writerow([
                        page_data["page_name"],
                        page_data["total_issues"],
                        main_issues,
                        modal_issues,
                        ", ".join(details) if details else "N/A"
                    ])
            
            logger.info(f"Summary report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return None
            
    def generate_json_report(self, missing_translations: Dict[str, Any],
                           filename: Optional[str] = None) -> Optional[str]:
        """
        Generate a JSON report of missing translations
        
        Args:
            missing_translations (Dict[str, Any]): Dictionary of missing translations by page and section
            filename (Optional[str]): Optional filename for the report
            
        Returns:
            Optional[str]: Path to the generated report, or None if generation failed
        """
        try:
            # Create filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"localization_report_{timestamp}.json"
                
            # Create full path
            report_path = self.reports_dir / filename
            
            # Create report structure
            report_data = {
                "generated_at": datetime.now().isoformat(),
                "missing_translations": missing_translations,
                "summary": {
                    "total_pages": len(missing_translations),
                    "total_issues": sum(
                        sum(len(items) for items in sections.values())
                        for sections in missing_translations.values()
                    )
                }
            }
            
            # Add page summaries
            page_summaries = []
            for page_name, sections in missing_translations.items():
                page_total = sum(len(items) for items in sections.values())
                page_summaries.append({
                    "page_name": page_name,
                    "total_issues": page_total,
                    "section_counts": {section: len(items) for section, items in sections.items()}
                })
                
            # Sort by most issues first
            page_summaries.sort(key=lambda x: x["total_issues"], reverse=True)
            report_data["summary"]["pages"] = page_summaries
            
            # Write JSON file
            with open(report_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(report_data, jsonfile, indent=2, ensure_ascii=False)
                
            logger.info(f"JSON report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            return None
            
    def generate_html_report(self, missing_translations: Dict[str, Any], screenshots: List[Dict[str, Any]], filename: str) -> str:
        """
        Generate an HTML report with screenshots and missing translations
        
        Args:
            missing_translations (Dict[str, Any]): Dictionary of missing translations
            screenshots (List[Dict[str, Any]]): List of screenshot information
            filename (str): Name of the HTML file to generate
            
        Returns:
            str: Path to the generated HTML file
        """
        try:
            # Define hardcoded directories and paths
            report_dir = self.session_dir / "reports" if self.session_dir else Path("reports")
            report_path = report_dir / filename
            
            # Create assets directory for screenshots
            assets_dir = report_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Copy screenshots to assets directory
            screenshot_paths = {}
            for screenshot in screenshots:
                src_path = Path(screenshot["path"])
                dest_path = assets_dir / src_path.name
                shutil.copy2(src_path, dest_path)
                page_name = screenshot["page"]
                modal_name = screenshot.get("modal")
                key = f"{page_name}_{modal_name}" if modal_name else page_name
                screenshot_paths[key] = dest_path.name

            # Basic HTML template with everything hardcoded
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>LocaLocaLocalize Report</title>
                <style>
                    :root {
                        --primary: #1e6c65;
                        --primary-dark: #16514c;
                        --accent: #d05819;
                        --text: #333333;
                        --text-light: #555555;
                        --bg-light: #f9f9f9;
                        --border-light: #e0e0e0;
                    }
                    
                    body {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: var(--text);
                        background-color: var(--bg-light);
                        margin: 0;
                        padding: 20px;
                    }
                    
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                        padding: 30px;
                    }
                    
                    .report-header {
                        position: sticky;
                        top: 0;
                        background: white;
                        padding: 15px 0;
                        border-bottom: 1px solid var(--border-light);
                        margin-bottom: 20px;
                        z-index: 10;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    
                    .report-title {
                        display: flex;
                        align-items: center;
                        gap: 15px;
                    }
                    
                    .timestamp {
                        font-size: 14px;
                        color: var(--text-light);
                        background-color: var(--bg-light);
                        padding: 5px 10px;
                        border-radius: 4px;
                        border: 1px solid var(--border-light);
                    }
                    
                    .nav-links {
                        display: flex;
                        gap: 15px;
                    }
                    
                    .nav-link {
                        color: var(--primary);
                        text-decoration: none;
                        font-weight: 500;
                        padding: 5px 10px;
                        border-radius: 4px;
                        transition: background-color 0.2s;
                    }
                    
                    .nav-link:hover {
                        background-color: var(--bg-light);
                    }
                    
                    .modal {
                        display: none;
                        position: fixed;
                        z-index: 1000;
                        padding-top: 50px;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(17, 17, 97, 0.9);
                    }
                    
                    .modal-content {
                        margin: auto;
                        display: block;
                        max-width: 90%;
                        max-height: 90vh;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                        border-radius: 4px;
                    }
                    
                    .close {
                        position: absolute;
                        right: 35px;
                        top: 15px;
                        color: white;
                        font-size: 40px;
                        font-weight: bold;
                        cursor: pointer;
                        transition: color 0.2s;
                    }
                    
                    .close:hover {
                        color: #ccc;
                    }
                    
                    #caption {
                        margin: auto;
                        display: block;
                        width: 80%;
                        max-width: 700px;
                        text-align: center;
                        color: white;
                        padding: 10px 0;
                        height: auto;
                        font-size: 18px;
                    }
                    
                    .screenshot-img {
                        cursor: pointer;
                        transition: all 0.3s;
                        max-width: 100%;
                        border-radius: 4px;
                    }
                    
                    .screenshot-img:hover {
                        opacity: 0.9;
                        transform: scale(1.01);
                    }
                    
                    h1 {
                        color: var(--primary);
                        margin-top: 0;
                        font-size: 32px;
                        font-weight: 600;
                        border-bottom: 2px solid var(--border-light);
                        padding-bottom: 10px;
                    }
                    
                    h2 {
                        color: white;  /* Changed to white for better visibility in headers */
                        margin-top: 0;
                        font-weight: 600;
                    }
                    
                    h3 {
                        color: #2c3e50;
                        font-size: 20px;
                        font-weight: 500;
                    }
                    
                    .page-section {
                        margin-bottom: 40px;
                        border: 1px solid #e0e0e0;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                        transition: box-shadow 0.3s;
                    }
                    
                    .page-section:hover {
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    }
                    
                    .page-header {
                        background-color: var(--primary);
                        color: white;
                        padding: 16px 24px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 4px solid var(--primary-dark);
                    }
                    
                    .page-header span {
                        font-size: 16px;
                        background-color: rgba(255, 255, 255, 0.2);
                        padding: 5px 12px;
                        border-radius: 20px;
                        font-weight: 500;
                    }
                    
                    .page-content {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 24px;
                        padding: 24px;
                        background-color: white;
                    }
                    
                    .screenshot {
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
                        position: relative;
                    }
                    
                    .screenshot:before {
                        content: 'Click to enlarge';
                        position: absolute;
                        bottom: 10px;
                        right: 10px;
                        background-color: rgba(0, 0, 0, 0.6);
                        color: white;
                        padding: 5px 10px;
                        border-radius: 4px;
                        font-size: 12px;
                        opacity: 0;
                        transition: opacity 0.3s;
                        z-index: 1;
                    }
                    
                    .screenshot:hover:before {
                        opacity: 1;
                    }
                    
                    .issues-list {
                        background: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
                    }
                    
                    .issue {
                        margin-bottom: 12px;
                        padding: 14px;
                        background: var(--bg-light);
                        border-radius: 8px;
                        border-left: 4px solid var(--accent);
                        position: relative;
                        transition: transform 0.2s, box-shadow 0.2s;
                    }
                    
                    .issue:hover {
                        transform: translateX(3px);
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    }
                    
                    .issue-text {
                        font-weight: 600;
                        color: var(--accent);
                        font-size: 16px;
                        margin-bottom: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    }
                    
                    .issue-text:after {
                        content: 'Not Translated';
                        font-size: 11px;
                        font-weight: 500;
                        background-color: var(--accent);
                        color: white;
                        padding: 3px 8px;
                        border-radius: 12px;
                        margin-left: 8px;
                    }
                    
                    .summary {
                        background: white;
                        padding: 24px;
                        margin-bottom: 30px;
                        border-radius: 12px;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                        border: 1px solid #e0e0e0;
                    }
                    
                    .stats {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 24px;
                        margin-top: 20px;
                    }
                    
                    .stat-card {
                        background: linear-gradient(to bottom right, #f9f9f9, #f0f0f0);
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        border: 1px solid #e0e0e0;
                        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
                        transition: transform 0.3s;
                    }
                    
                    .stat-card:hover {
                        transform: translateY(-3px);
                    }
                    
                    .stat-number {
                        font-size: 36px;
                        font-weight: bold;
                        color: var(--primary);
                        margin-bottom: 8px;
                    }
                    
                    .stat-label {
                        font-size: 16px;
                        color: var(--text-light);
                        font-weight: 500;
                    }
                    
                    @media (max-width: 768px) {
                        .page-content {
                            grid-template-columns: 1fr;
                        }
                        
                        .container {
                            padding: 15px;
                        }
                    }
                </style>
                <script>
                function openModal(imgSrc, caption) {
                    var modal = document.getElementById("imageModal");
                    var modalImg = document.getElementById("modalImage");
                    var captionText = document.getElementById("caption");
                    
                    modal.style.display = "block";
                    modalImg.src = imgSrc;
                    captionText.innerHTML = caption;
                }
                
                function closeModal() {
                    document.getElementById("imageModal").style.display = "none";
                }
                
                window.onclick = function(event) {
                    var modal = document.getElementById("imageModal");
                    if (event.target == modal) {
                        modal.style.display = "none";
                    }
                }
                </script>
            </head>
            <body>
                <!-- Image Modal -->
                <div id="imageModal" class="modal">
                    <span class="close" onclick="closeModal()">&times;</span>
                    <img class="modal-content" id="modalImage">
                    <div id="caption"></div>
                </div>

                <div class="container">
                    <div class="report-header">
                        <div class="report-title">
                            <h1>LocaLocaLocalize Report</h1>
                            <div class="timestamp">Generated: {current_time}</div>
                        </div>
                        <div class="nav-links">
                            <a href="#summary" class="nav-link">Summary</a>
                            <a href="#pages" class="nav-link">Pages</a>
                        </div>
                    </div>
            """
            
            # Add current timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add summary section with an ID
            html_content += """
                    <div id="summary" class="summary">
                        <h2>Summary</h2>
                        <div class="stats">
            """
            
            # Calculate total issues
            total_issues = 0
            for page_data in missing_translations.values():
                for section_items in page_data.values():
                    if isinstance(section_items, list):
                        total_issues += len(section_items)
            
            # Add summary statistics
            html_content += f"""
                            <div class="stat-card">
                                <div class="stat-number">{len(missing_translations)}</div>
                                <div class="stat-label">Pages Analyzed</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{total_issues}</div>
                                <div class="stat-label">Total Issues Found</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{len(screenshots)}</div>
                                <div class="stat-label">Screenshots Taken</div>
                            </div>
                        </div>
                    </div>
            """
            
            # Add a header for the pages section
            html_content += """
                    <div id="pages">
                        <h2>Pages with Issues</h2>
                    </div>
            """
            
            # Add page sections with screenshots
            for page_name, page_data in missing_translations.items():
                screenshot_key = page_name
                screenshot_path = screenshot_paths.get(screenshot_key, "")
                
                # Get main page issues
                main_issues = page_data.get("main", [])
                issue_count = len(main_issues)
                
                html_content += f"""
                <div class="page-section">
                    <div class="page-header">
                        <h2>{page_name}</h2>
                        <span>{issue_count} issues found</span>
                    </div>
                    <div class="page-content">
                        <div class="screenshot">
                            <img src="assets/{screenshot_path}" alt="{page_name} screenshot" class="screenshot-img" 
                                 onclick="openModal('assets/{screenshot_path}', '{page_name}')">
                        </div>
                        <div class="issues-list">
                            <h3>Missing Translations</h3>
                """
                
                # Add page issues
                if main_issues:
                    for issue in main_issues:
                        html_content += f"""
                                <div class="issue">
                                    <div class="issue-text">{issue.get("text", "")}</div>
                                    <div>Detected as: {issue.get("language", "English")}</div>
                                    <div>Confidence: {issue.get("confidence", "N/A")}</div>
                                </div>
                        """
                else:
                    html_content += "<p>No issues found</p>"
                
                html_content += """
                            </div>
                        </div>
                    </div>
                """
                
                # Add modal sections
                for modal_name, modal_issues in page_data.items():
                    if modal_name == "main" or not isinstance(modal_issues, list) or not modal_issues:
                        continue
                        
                    modal_key = f"{page_name}_{modal_name}"
                    modal_screenshot = screenshot_paths.get(modal_key, "")
                    
                    if modal_screenshot:
                        html_content += f"""
                            <div class="page-section">
                                <div class="page-header">
                                    <h2>{page_name} - {modal_name}</h2>
                                    <span>{len(modal_issues)} issues found</span>
                                </div>
                                <div class="page-content">
                                    <div class="screenshot">
                                        <img src="assets/{modal_screenshot}" alt="{modal_name} screenshot" class="screenshot-img"
                                             onclick="openModal('assets/{modal_screenshot}', '{page_name} - {modal_name}')">
                                    </div>
                                    <div class="issues-list">
                                        <h3>Missing Translations</h3>
                        """
                        
                        for issue in modal_issues:
                            html_content += f"""
                                        <div class="issue">
                                            <div class="issue-text">{issue.get("text", "")}</div>
                                            <div>Detected as: {issue.get("language", "English")}</div>
                                            <div>Confidence: {issue.get("confidence", "N/A")}</div>
                                        </div>
                            """
                            
                        html_content += """
                                    </div>
                                </div>
                            </div>
                        """
            
            # Close HTML tags
            html_content += """
                </div>
            </body>
            </html>
            """
            
            # Write HTML file
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open the report in the default browser
            try:
                absolute_path = report_path.resolve()
                logger.info(f"Opening HTML report in browser: file://{absolute_path}")
                file_url = f'file://{absolute_path}'
                
                webbrowser.open(file_url)
                logger.info("Successfully opened browser")
            except Exception as e:
                logger.error(f"Error opening browser: {e}")
                
            logger.info(f"Generated HTML report: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return ""
            
    def generate_all_reports(self, missing_translations: Dict[str, Any]) -> List[str]:
        """
        Generate all report types
        
        Args:
            missing_translations (Dict[str, Any]): Dictionary of missing translations by page and section
            
        Returns:
            List[str]: List of paths to the generated reports
        """
        reports = []
        
        # Generate timestamp for consistent filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate CSV report
        csv_path = self.generate_report(
            missing_translations, 
            f"localization_report_{timestamp}.csv"
        )
        if csv_path:
            reports.append(csv_path)
            
        # Generate summary report
        summary_path = self.generate_summary_report(
            missing_translations,
            f"localization_report_{timestamp}_summary.csv"
        )
        if summary_path:
            reports.append(summary_path)
            
        # Check if JSON report is enabled
        if self.config.get('output.enable_json_report', True):  # Default to True
            json_path = self.generate_json_report(
                missing_translations,
                f"localization_report_{timestamp}.json"
            )
            if json_path:
                reports.append(json_path)
        
        # Note: HTML report is generated separately with screenshots
        # in the main run() method
                
        return reports 