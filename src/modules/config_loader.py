#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Loader Module

This module handles loading and accessing configuration settings
for the LocaLocaLocalize tool.
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Setup logging
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for the LocaLocaLocalize tool.
    Handles loading and accessing configuration settings.
    """
    
    _instance = None
    _config = {}
    _loaded = False
    
    def __new__(cls):
        """
        Singleton pattern implementation to ensure only one config instance exists
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
        
    def load(self, config_path: Optional[str] = None) -> bool:
        """
        Load configuration from a YAML file
        
        Args:
            config_path (Optional[str]): Path to the config file, or None to use environment variable
            
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        # If config is already loaded, return True
        if self._loaded:
            return True
            
        try:
            # Determine config path
            if not config_path:
                # Try to get from environment variable
                config_path = os.environ.get('LOCALOCALOCALIZE_CONFIG', 'config/config.yaml')
                
            config_file = Path(config_path)
            
            if not config_file.exists():
                logger.error(f"Configuration file not found: {config_path}")
                return False
                
            logger.info(f"Loading configuration from: {config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
                
            self._loaded = True
            
            # Validate configuration
            valid = self._validate_config()
            
            # Create required directories
            self._create_directories()
            
            return valid
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
            
    def _validate_config(self) -> bool:
        """
        Validate the loaded configuration
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # Check for required sections
        required_sections = ['application', 'browser', 'ocr']
        for section in required_sections:
            if section not in self._config:
                logger.error(f"Missing required configuration section: {section}")
                return False
                
        # Validate application section
        app_config = self._config.get('application', {})
        if not app_config.get('base_url'):
            logger.warning("No base_url specified in application configuration")
            
        # OCR configuration
        ocr_config = self._config.get('ocr', {})
        ocr_engine = ocr_config.get('engine', 'easyocr')
        
        # If using Google Vision API, check for API key configuration
        if ocr_engine == 'google_vision':
            api_key = ocr_config.get('api_key', '') or os.environ.get('GOOGLE_VISION_API_KEY', '')
            if not api_key:
                logger.warning("Google Vision API selected but no API key provided")
                
        # Validate language settings
        if not ocr_config.get('target_language'):
            logger.warning("No target language specified in OCR configuration")
            
        return True
        
    def _create_directories(self) -> None:
        """
        Create required directories from configuration
        """
        # Create screenshot directory
        screenshot_dir = Path(self.get('output.screenshot_dir', './screenshots'))
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Create reports directory
        reports_dir = Path(self.get('output.reports_dir', './reports'))
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        logs_dir = Path(self.get('output.logs_dir', './logs'))
        logs_dir.mkdir(parents=True, exist_ok=True)
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-notation key
        
        Args:
            key (str): The dot-notation key for the configuration value
            default (Any): Default value to return if key not found
            
        Returns:
            Any: The configuration value or default if not found
        """
        if not self._loaded:
            logger.warning("Attempting to access configuration before loading")
            self.load()
            
        # Split the key by dots
        parts = key.split('.')
        
        # Start with the root config
        value = self._config
        
        # Navigate through the parts
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by dot-notation key
        
        Args:
            key (str): The dot-notation key for the configuration value
            value (Any): Value to set
        """
        if not self._loaded:
            logger.warning("Attempting to modify configuration before loading")
            self.load()
            
        # Split the key by dots
        parts = key.split('.')
        
        # Navigate to the appropriate section
        config = self._config
        for i, part in enumerate(parts[:-1]):
            if part not in config:
                config[part] = {}
            config = config[part]
            
        # Set the value
        config[parts[-1]] = value
        
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration
        
        Returns:
            Dict[str, Any]: The entire configuration dictionary
        """
        if not self._loaded:
            logger.warning("Attempting to access configuration before loading")
            self.load()
            
        return self._config

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration values
        
        Args:
            updates (Dict[str, Any]): Dictionary of configuration updates using dot notation
        """
        if not self._loaded:
            logger.warning("Attempting to update configuration before loading")
            self.load()
            
        for key, value in updates.items():
            parts = key.split('.')
            current = self._config
            
            # Navigate to the correct nested level
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
                
            # Set the value
            current[parts[-1]] = value
            
        logger.info("Configuration updated successfully")

# For backward compatibility
def get_config() -> Dict[str, Any]:
    """
    Get the entire configuration
    
    Returns:
        Dict[str, Any]: The entire configuration dictionary
    """
    config = Config()
    return config.get_all()

def get(key: str, default: Any = None) -> Any:
    """
    Get a configuration value by dot-notation key
    
    Args:
        key (str): The dot-notation key for the configuration value
        default (Any): Default value to return if key not found
        
    Returns:
        Any: The configuration value or default if not found
    """
    config = Config()
    return config.get(key, default)


if __name__ == "__main__":
    # Simple test if run directly
    try:
        config = get_config()
        print(f"Loaded configuration for: {get('application.name')}")
        print(f"Base URL: {get('application.base_url')}")
        print(f"Number of pages: {len(get('pages', []))}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 