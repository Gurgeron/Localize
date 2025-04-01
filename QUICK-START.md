# LocaLocaLocalize Quick Start Guide

This guide will help you get started with LocaLocaLocalize, a tool for finding localization issues in web applications.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Git (optional, for cloning the repository)

## Installation

### On Linux/Mac

1. Clone or download the repository:
   ```
   git clone https://github.com/yourusername/LocaLocaLocalize.git
   cd LocaLocaLocalize
   ```

2. Run the installation script:
   ```
   ./install.sh
   ```

3. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

### On Windows

1. Clone or download the repository:
   ```
   git clone https://github.com/yourusername/LocaLocaLocalize.git
   cd LocaLocaLocalize
   ```

2. Run the installation script:
   ```
   install.bat
   ```

3. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```

## Configuration

1. Edit `config/config.yaml` to configure:
   - Target website URL (application.base_url)
   - Pages to scan
   - Browser settings
   - OCR settings
   
2. (Optional) Set up API keys or credentials:
   - Edit `.env` to add your credentials or API keys
   - All secrets are stored locally and not shared

## Running the Tool

1. Ensure your virtual environment is activated
2. Run the main script:
   ```
   python src/main.py
   ```

3. Follow the prompts to:
   - Log in manually to the application
   - Set the language to French
   - Press Enter to start the automated scanning process

## Understanding the Results

After the scan completes:
1. Check the `reports/` directory for CSV files with detected issues
2. Each issue will include:
   - Page name
   - Modal name (if applicable)
   - Text snippet in English
   - Screenshot filename for reference

3. Check the summary report for:
   - Total pages/modals visited
   - Statistics on issues found
   - Top pages with issues

## Advanced Usage

Run with debug logging:
```
python src/main.py --debug
```

Run in headless mode (no visible browser):
```
python src/main.py --headless
```

Use a different config file:
```
python src/main.py --config path/to/config.yaml
```

## Troubleshooting

If you encounter issues:
1. Check the logs in the `logs/` directory
2. Ensure your Python version is 3.8 or higher
3. Try reinstalling dependencies with `pip install -r requirements.txt`
4. Ensure you have the right privileges to run Playwright

## Next Steps

To customize the tool for your needs:
1. Edit page configurations in `config/config.yaml`
2. Add more pages and modals to the config
3. Adjust OCR and language detection settings as needed 