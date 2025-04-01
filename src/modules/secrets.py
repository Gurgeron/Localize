#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Secrets Module

This module handles loading and accessing secrets like API keys.
It uses environment variables or .env files for secure storage.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Import our modules
from .config_loader import get

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecretsManager:
    """
    SecretsManager class for loading and accessing secrets
    """
    
    def __init__(self, env_path: str = ".env"):
        """
        Initialize the SecretsManager
        
        Args:
            env_path (str): Path to the .env file
        """
        self.env_path = env_path
        self.loaded = False
        
        # Load secrets from .env file
        self._load_secrets()
    
    def _load_secrets(self) -> None:
        """
        Load secrets from .env file or environment variables
        """
        try:
            # Check if .env file exists
            if Path(self.env_path).exists():
                # Load .env file
                load_dotenv(self.env_path)
                logger.info(f"Loaded secrets from {self.env_path}")
                self.loaded = True
            else:
                logger.warning(f".env file not found at {self.env_path}, using existing environment variables")
                # Still consider it loaded, we'll use environment variables
                self.loaded = True
                
        except Exception as e:
            logger.error(f"Error loading secrets: {e}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get an API key for a service
        
        Args:
            service (str): Name of the service (e.g., 'google_cloud_vision')
            
        Returns:
            Optional[str]: API key, or None if not found
        """
        # Try to get API key from environment variables
        env_var_name = f"{service.upper()}_API_KEY"
        api_key = os.getenv(env_var_name)
        
        if api_key:
            logger.debug(f"Found API key for {service} in environment variables")
            return api_key
            
        # Try to get API key from config
        config_key = get(f'api_keys.{service}', '')
        if config_key:
            logger.debug(f"Found API key for {service} in config")
            return config_key
            
        logger.warning(f"API key for {service} not found")
        return None
    
    def get_credentials(self) -> Dict[str, Optional[str]]:
        """
        Get credentials for login
        
        Returns:
            Dict[str, Optional[str]]: Dictionary with username and password
        """
        # Try to get credentials from environment variables
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        
        # If not found, try to get from config
        if not username:
            username = get('credentials.username', '')
        if not password:
            password = get('credentials.password', '')
            
        return {
            "username": username,
            "password": password
        }


# Singleton instance of the secrets manager
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """
    Get the secrets manager instance
    
    Returns:
        SecretsManager: The secrets manager instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager

def get_api_key(service: str) -> Optional[str]:
    """
    Get an API key for a service
    
    Args:
        service (str): Name of the service (e.g., 'google_cloud_vision')
        
    Returns:
        Optional[str]: API key, or None if not found
    """
    return get_secrets_manager().get_api_key(service)

def get_credentials() -> Dict[str, Optional[str]]:
    """
    Get credentials for login
    
    Returns:
        Dict[str, Optional[str]]: Dictionary with username and password
    """
    return get_secrets_manager().get_credentials()


# Testing function for direct module execution
def main():
    """Main function for testing the secrets module"""
    print("Testing Secrets Module")
    
    # Test API key retrieval
    for service in ['google_cloud_vision', 'aws_textract', 'azure_cognitive']:
        api_key = get_api_key(service)
        if api_key:
            print(f"Found API key for {service}: {api_key[:4]}{'*' * (len(api_key) - 4)}")
        else:
            print(f"No API key found for {service}")
    
    # Test credentials retrieval
    credentials = get_credentials()
    if credentials["username"] and credentials["password"]:
        print(f"Found credentials: {credentials['username']} / {'*' * len(credentials['password'])}")
    else:
        print("No credentials found")

if __name__ == "__main__":
    main() 