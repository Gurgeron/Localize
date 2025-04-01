# LocaLocaLocalize Changelog

All notable changes to the LocaLocaLocalize project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.4] - 2024-04-02

### Fixed
- Completely rewrote HTML report generation function to resolve persistent issues
- Removed all variable interpolation and replaced with hardcoded values
- Fixed image modal functionality with direct event handlers
- Enhanced error handling for report generation
- Improved browser opening reliability
- Fixed issue with missing content or invalid data in reports
- Added defensive coding for missing screenshot references

## [1.2.3] - 2024-04-02

### Fixed
- Fixed HTML report generation by removing Python variable interpolation for color variables
- Resolved the persistent issue with HTML reports not being generated
- Simplified color definition approach to avoid naming conflicts
- Ensured consistent browser opening of reports when generated

## [1.2.2] - 2024-04-02

### Fixed
- Fixed HTML report generation by hardcoding CSS variables directly in the template
- Resolved the "name 'primary' is not defined" error that was preventing HTML report creation
- Ensured full compatibility with CSV, HTML, and JSON report formats

## [1.2.1] - 2024-04-02

### Fixed
- Fixed HTML report to work correctly with the new OCR data structure
- Improved CSV report generation for better spreadsheet compatibility
- Enhanced error handling in report opening mechanism
- Fixed issue with empty modal sections in reports
- Added more detailed language and confidence information to reports

## [1.2.0] - 2024-04-02

### Fixed
- Fixed HTML report generation with proper color variables
- Fixed report generation in generate_all_reports method
- Corrected handling of HTML report generation

## [1.1.9] - 2024-04-02

### Changed
- Improved OCR text processing to use dedicated screenshot processing method
- Enhanced language detection with better error handling
- Streamlined missing translation detection process
- Removed redundant text block analysis step

## [1.1.8] - 2024-04-02

### Fixed
- Fixed OCR method name mismatch (process_image -> extract_text_from_image)
- Removed incorrect async/await usage for OCR text extraction
- Improved error handling in OCR processing

## [1.1.7] - 2024-04-02

### Added
- Page load verification before taking screenshots
- Comprehensive page load checks including:
  - Network idle state
  - DOM content loaded
  - Loading indicators disappeared
  - Dynamic content loaded
- Updated color scheme with new brand colors:
  - Primary: #111161 (Navy Blue)
  - Secondary: #d05819 (Orange)
  - Accent: #0c534d (Teal)
  - Background: #f0eee8 (Off-white)

### Changed
- Enhanced screenshot capture with load verification
- Improved error handling for page load issues
- Updated HTML report styling with new color palette
- Enhanced visual hierarchy in reports

## [1.1.6] - 2024-04-02

### Added
- Automatic browser opening of HTML reports after generation
- Interactive image modal for full-size screenshot viewing
- Improved screenshot interaction with hover effects
- Better user experience with clickable images

### Changed
- Enhanced HTML report styling for better image interaction
- Updated screenshot display to support modal viewing
- Improved report accessibility with interactive elements

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