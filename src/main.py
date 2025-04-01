#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LocaLocaLocalize - Main Module

This is the main entry point for the LocaLocaLocalize tool, which automates
localization testing for web applications.

The tool captures screenshots, extracts text using OCR,
identifies non-localized strings, and generates reports.

Enhanced version with automatic page discovery, intelligent modal detection,
and improved OCR using Google Cloud Vision API.
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from modules.config_loader import Config
from modules.browser import BrowserController
from modules.ocr import OCRProcessor
from modules.reporter import ReportGenerator

class LocaLocaLocalize:
    """Main class for the LocaLocaLocalize tool"""
    
    def __init__(self):
        """Initialize the LocaLocaLocalize application"""
        self.config = Config()
        self.browser = BrowserController()
        self.ocr_processor = None
        self.reporter = None
        self.screenshots = []
        self.text_blocks = {}
        self.missing_translations = {}
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = None
        
        # Create session directories immediately
        self.create_session_directories()
        
        # Setup logging after creating directories
        self.setup_logging()
        
    def setup_logging(self) -> None:
        """Setup logging configuration"""
        log_file = self.session_dir / "logs" / "localization.log"
        
        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create file handler
        file_handler = logging.FileHandler(str(log_file))
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Get the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add our handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Get our module logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logging initialized for session: %s", self.session_timestamp)
        self.logger.info("Log file: %s", log_file)

# ... existing code ...