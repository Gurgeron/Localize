# LocaLocaLocalize

An advanced automated localization testing tool for web applications. Ensure your internationalized UI is properly localized without manual inspection.

![LocaLocaLocalize Logo](assets/logo.png)

## 🌍 Overview

LocaLocaLocalize is a powerful tool designed to automate the process of localization testing for web applications. It navigates through your web application, captures screenshots, extracts text using OCR, detects non-localized strings, and generates comprehensive reports. With minimal configuration, you can quickly identify areas where localization is missing or incorrect.

## ✨ Features

- **Automatic Browser Testing**: Automates browser interactions using Playwright to test your application in multiple languages
- **Smart Page and Modal Discovery**: Automatically discovers and tests pages and modals without requiring manual configuration
- **High-Quality OCR**: Extracts text from screenshots using either EasyOCR or Google Cloud Vision API
- **Intelligent Language Detection**: Identifies non-localized text with advanced language detection algorithms and custom dictionaries
- **Comprehensive Reporting**: Generates detailed reports in multiple formats (CSV, HTML, JSON) with summary statistics
- **Highly Configurable**: Extensive configuration options via YAML to customize every aspect of the testing process
- **Screenshot Management**: Automatically captures and organizes screenshots for later visual verification

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/localocalocalize.git
   cd localocalocalize
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install browser drivers (first time only):
   ```bash
   python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().stop()"
   playwright install
   ```

## 📋 Usage

### Basic Usage

1. Configure your application settings in `config/config.yaml`
2. Run the tool:
   ```bash
   python src/main.py
   ```

3. The tool will:
   - Launch a browser
   - Prompt you to log in manually (you can interact with the browser)
   - Automatically navigate through configured pages
   - Discover additional pages and modals if enabled
   - Take screenshots
   - Process images with OCR
   - Detect non-localized strings
   - Generate reports

### Configuration

Create a `config/config.yaml` file (you can copy `config/config.sample.yaml` as a starting point). Here's an overview of the configuration options:

#### Application Settings
```yaml
application:
  base_url: "https://your-app.com"
  login_url: "https://your-app.com/login"
  headless: false
  default_timeout: 30000
  stabilization_time: 1000
  auto_discover_modals: true
  auto_discover_pages: false
```

#### Browser Settings
```yaml
browser:
  type: "chromium"  # chromium, firefox, or webkit
  width: 1920
  height: 1080
  user_agent: ""  # Optional custom user agent
```

#### Page Definitions
```yaml
pages:
  - name: "Dashboard"
    url: "/dashboard"
    modals:
      - name: "Settings"
        selector: "button.settings-button"
  - name: "Profile"
    url: "/profile"
```

#### OCR Settings
```yaml
ocr:
  engine: "easyocr"  # easyocr or google_vision
  target_language: "fr"
  api_key: ""  # For Google Cloud Vision
  
  # Advanced OCR settings
  easyocr:
    languages: ["fr", "en"]
    gpu: false
    
  google_vision:
    batch_size: 5
```

#### Complete Configuration
See the `config/config.yaml` file for complete configuration options.

### Using Google Cloud Vision API

For more accurate text extraction, you can use the Google Cloud Vision API:

1. Create a Google Cloud account and enable the Vision API
2. Create an API key
3. Add the API key to your configuration:
   ```yaml
   ocr:
     engine: "google_vision"
     api_key: "YOUR_API_KEY"
   ```
   
   Or set it as an environment variable:
   ```bash
   export GOOGLE_VISION_API_KEY=YOUR_API_KEY
   ```

### Automatic Page and Modal Discovery

LocaLocaLocalize can automatically discover pages and modals:

```yaml
application:
  auto_discover_modals: true  # Find modals on each page
  auto_discover_pages: true   # Discover new pages during navigation
```

## 📊 Reports

LocaLocaLocalize generates detailed reports:

- **CSV Reports**: Main report with all missing translations
- **Summary CSV**: Overview of issues by page and section
- **HTML Report**: Interactive report with detailed statistics and visualizations
- **JSON Report**: Structured data for programmatic processing

Reports are saved in the `reports` directory.

## 📷 Screenshots

Screenshots are saved in the `screenshots` directory, organized by:
- Page screenshots: `screenshots/PageName_TIMESTAMP.png`
- Modal screenshots: `screenshots/modals/ModalName_TIMESTAMP.png`

## 🔧 Troubleshooting

### Import Errors

If you encounter a `ModuleNotFoundError` when running the tool, this is usually related to Python's module resolution:

```
ModuleNotFoundError: No module named 'src'
```

**Solution**:
1. Use the provided `run.sh` script which properly sets the PYTHONPATH:
   ```bash
   ./run.sh
   ```

2. If you're running the script directly, make sure to set PYTHONPATH correctly:
   ```bash
   export PYTHONPATH=$(pwd):$PYTHONPATH
   python src/main.py
   ```

### Missing Dependencies

If you see errors about missing modules like `requests` or other dependencies:

**Solution**:
1. Make sure you've installed all the required packages:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Update the Playwright browsers:
   ```bash
   playwright install
   ```

## 🛠️ Advanced Usage

### Command-line Arguments

```bash
python src/main.py --config path/to/custom/config.yaml
```

### Environment Variables

- `LOCALOCALOCALIZE_CONFIG`: Path to the configuration file
- `GOOGLE_VISION_API_KEY`: API key for Google Cloud Vision

## 📝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

If you have any questions or need assistance, please open an issue on GitHub. 