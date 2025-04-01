# LocaLocaLocalize Changelog

All notable changes to the LocaLocaLocalize project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.5] - 2024-04-02

### Added
- Enhanced logging system with proper file and console handlers
- Detailed session logging with timestamps and file paths
- Automatic handler cleanup to prevent duplicate logging

### Fixed
- Empty log file issue by properly configuring file handlers
- Logger initialization sequence to ensure all logs are captured

## [1.1.4] - 2024-04-02

### Added
- Configuration update method to allow dynamic configuration changes
- Better error handling for configuration updates
- Session-specific logging with both file and console output
- Improved logging initialization to ensure logs are captured from startup

### Fixed
- Configuration update functionality that was causing runtime errors
- Logging setup to properly use session directories

## [1.1.3] - 2024-04-02

### Added
- Session-based organization: Each test run now has its own directory with screenshots and reports
- Beautiful HTML report with screenshots next to detected issues
- Improved language detection to focus only on English vs French
- Extended dictionary of common hospitality terms to reduce false positives

### Changed
- Reorganized output structure for better organization and clarity
- Enhanced language detection algorithm to reduce false positives from other languages
- Updated report styling with a modern, clean design
- Improved screenshot management with better organization

## [1.1.2] - 2024-04-02

### Fixed
- Fixed Python module import error by correcting import paths in main.py
- Updated run.sh script to properly set PYTHONPATH for consistent module resolution

## [1.1.1] - 2024-04-02

### Added
- Google Cloud Vision API key integration for production use
- Improved OCR text extraction with cloud-based processing
- Enhanced run script with automatic API key configuration

### Changed
- Updated OCR module to prioritize Google Cloud Vision when available
- Improved language detection for higher accuracy
- Updated configuration to use more consistent naming conventions

## [1.1.0] - 2024-04-01

### Added
- Google Cloud Vision API integration for more accurate OCR text extraction
- Automatic page discovery feature to find and test pages without manual configuration
- Intelligent modal detection to automatically find and test modals on pages
- Custom dictionary for hospitality terms to improve language detection accuracy
- HTML and JSON report formats in addition to CSV reports
- Enhanced summary reporting with detailed statistics
- Configuration validation and better error handling

### Changed
- Completely refactored the code architecture for better maintainability
- Improved browser module with smarter navigation and element detection
- Enhanced OCR module with support for multiple OCR engines
- Updated configuration loader with singleton pattern and better validation
- Reorganized project structure and improved modularity
- Expanded configuration options with more customization choices
- Improved logging and error reporting

### Fixed
- Fixed language detection false positives for common industry terms
- Fixed modal handling to properly close modals after capturing
- Fixed issues with window sizing to prevent content overflow
- Improved error recovery during page navigation

## [1.0.0] - 2024-03-30

### Added
- Initial release of LocaLocaLocalize
- Basic browser automation with Playwright
- Screenshot capture of pages and modals
- OCR text extraction with EasyOCR
- Language detection to find non-localized text
- CSV report generation for localization issues
- Manual login flow with user prompting
- YAML-based configuration system
- Core modules implementation:
  - Browser automation with Playwright
    - Navigation to pages and modals
    - Screenshot capture functionality
    - Manual login handling
  - OCR implementation with EasyOCR
    - Text extraction from screenshots
    - Language detection functionality
  - CSV report generation and analysis
  - Configuration loading and validation
  - Secrets management with support for .env files
- Project documentation:
  - README.md with setup and usage instructions
  - Comprehensive docstrings and comments throughout the code
- Configuration:
  - Sample YAML configuration file
  - Environment variables management (.env.sample)
- Installation scripts:
  - Linux/Mac installation script (install.sh)
  - Windows installation script (install.bat)
- Setup files:
  - setup.py for package installation
  - requirements.txt with pinned dependencies
- Basic error handling and logging
- Extensible architecture for future features (date/time format validation) 