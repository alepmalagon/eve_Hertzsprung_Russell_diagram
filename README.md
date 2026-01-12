# EVE Online New Eden Hertzsprung-Russell Diagram Generator

This project generates a Hertzsprung-Russell (H-R) diagram for all stars in the New Eden cluster from EVE Online, using data from the ESI (EVE Swagger Interface) API.

**✅ Fully compatible with Windows PowerShell, Linux, and macOS**

## Overview

The Hertzsprung-Russell diagram is a fundamental tool in stellar astronomy that plots stellar luminosity against temperature (or spectral class). This project creates such a diagram specifically for the fictional universe of EVE Online, focusing on the New Eden cluster while excluding wormhole space (Aniokis galaxy).

## Features

- **Comprehensive Data Collection**: Fetches stellar data for all stars in New Eden using the ESI API
- **Intelligent Filtering**: Automatically excludes wormhole space systems (Aniokis galaxy)
- **Scientific Visualization**: Creates publication-quality H-R diagrams with proper astronomical conventions
- **Data Processing**: Cleans and validates stellar data, handles missing values and outliers
- **Multiple Visualizations**: Generates H-R diagram plus additional analysis plots
- **Caching System**: Saves API data locally to avoid redundant requests
- **Rate Limiting**: Respects ESI API rate limits with proper throttling

## Installation

### Linux/macOS

1. Clone the repository:
```bash
git clone https://github.com/alepmalagon/eve_Hertzsprung_Russell_diagram.git
cd eve_Hertzsprung_Russell_diagram
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Windows PowerShell

1. Clone the repository:
```powershell
git clone https://github.com/alepmalagon/eve_Hertzsprung_Russell_diagram.git
cd eve_Hertzsprung_Russell_diagram
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

**Note**: The project is fully compatible with Windows PowerShell and Command Prompt. All Python dependencies are cross-platform and work seamlessly on Windows.

## Usage

### Basic Usage

**Linux/macOS:**
```bash
python main.py
```

**Windows PowerShell:**
```powershell
python main.py
```

### Advanced Options

**Linux/macOS:**
```bash
# Force fresh data fetch (ignore cache)
python main.py --no-cache

# Specify custom cache file location
python main.py --cache-file data/my_stellar_data.json

# Specify custom output directory
python main.py --output-dir results/

# Test with limited sample size
python main.py --sample-size 1000
```

**Windows PowerShell:**
```powershell
# Force fresh data fetch (ignore cache)
python main.py --no-cache

# Specify custom cache file location
python main.py --cache-file data\my_stellar_data.json

# Specify custom output directory
python main.py --output-dir results\

# Test with limited sample size
python main.py --sample-size 1000
```

**Note**: Windows users can use either forward slashes (`/`) or backslashes (`\`) in file paths. The application automatically handles both formats.

### Command Line Arguments

- `--no-cache`: Force fresh data fetch from ESI API, ignoring any cached data
- `--cache-file`: Path to cache file for storing/loading stellar data (default: `data/stellar_data.json`)
- `--output-dir`: Directory for output files (default: `output/`)
- `--sample-size`: Limit processing to N stars for testing purposes

## Output Files

The program generates several files in the output directory:

### Main Outputs
- `hr_diagram_new_eden.png`: The main Hertzsprung-Russell diagram
- `results_summary.txt`: Summary of results and statistics

### Additional Analysis
- `spectral_distribution.png`: Distribution of spectral types
- `temperature_luminosity_correlation.png`: Temperature vs luminosity correlation plot
- `stellar_parameter_histograms.png`: Histograms of stellar parameters

### Data Files
- `processed_stellar_data.json`: Summary of processed data and statistics
- `data/stellar_data.json`: Cached raw stellar data from ESI API

## Data Sources

This project uses the EVE Online ESI API:
- **Base URL**: https://esi.evetech.net/
- **Stellar Data Endpoint**: `/universe/stars/{star_id}`
- **System Discovery**: `/universe/regions/`, `/universe/constellations/`, `/universe/systems/`

### Stellar Data Format

The ESI API provides stellar data in the following format:
```json
{
  "age": 0,
  "luminosity": 0,
  "name": "string",
  "radius": 0,
  "solar_system_id": 0,
  "spectral_class": "K2 V",
  "temperature": 0,
  "type_id": 0
}
```

## Technical Details

### Architecture

The project is structured into several modules:

- `src/esi_client.py`: Asynchronous ESI API client with rate limiting
- `src/data_processor.py`: Data cleaning, validation, and processing
- `src/hr_diagram.py`: H-R diagram generation and visualization
- `src/config.py`: Configuration settings and constants
- `main.py`: Main execution script

### Data Processing Pipeline

1. **System Discovery**: Identify all solar systems in New Eden regions
2. **Star Extraction**: Extract star IDs from each solar system
3. **Data Collection**: Fetch stellar data for all stars via ESI API
4. **Data Cleaning**: Remove invalid entries, handle outliers
5. **Data Enhancement**: Parse spectral classes, calculate derived properties
6. **Visualization**: Generate H-R diagram and analysis plots

### Galaxy Filtering

The project automatically excludes wormhole space (Aniokis galaxy) by filtering out region IDs in the range 11000001-11000031, which correspond to wormhole space regions.

## Scientific Accuracy

While EVE Online is a fictional universe, this project applies real astronomical principles:

- **H-R Diagram Conventions**: Temperature decreases left to right, luminosity on logarithmic scale
- **Spectral Classification**: Proper parsing of spectral types (O, B, A, F, G, K, M, etc.)
- **Stellar Physics**: Calculations of absolute magnitude, color indices, and mass estimates
- **Data Validation**: Removal of physically impossible values

## Performance Considerations

- **Rate Limiting**: Respects ESI's 150 requests/second limit
- **Asynchronous Processing**: Uses async/await for efficient API calls
- **Caching**: Saves API responses to avoid redundant requests
- **Progress Tracking**: Shows progress bars for long-running operations

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## Windows PowerShell Setup Guide

### Prerequisites

1. **Python Installation**: Ensure Python 3.8+ is installed and added to your PATH
   ```powershell
   python --version
   ```
   If Python is not found, download it from [python.org](https://www.python.org/downloads/) and make sure to check "Add Python to PATH" during installation.

2. **Git Installation**: Install Git for Windows from [git-scm.com](https://git-scm.com/download/win)

### Step-by-Step Setup

1. **Open PowerShell**: Press `Win + X` and select "Windows PowerShell" or "Windows Terminal"

2. **Navigate to your desired directory**:
   ```powershell
   cd C:\Users\YourUsername\Documents
   ```

3. **Clone the repository**:
   ```powershell
   git clone https://github.com/alepmalagon/eve_Hertzsprung_Russell_diagram.git
   cd eve_Hertzsprung_Russell_diagram
   ```

4. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

5. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

6. **Run the application**:
   ```powershell
   python main.py
   ```

### Easy Windows Setup (Alternative)

For an even simpler experience, use the included PowerShell script:

```powershell
# Clone and navigate to the project
git clone https://github.com/alepmalagon/eve_Hertzsprung_Russell_diagram.git
cd eve_Hertzsprung_Russell_diagram

# Run with automatic dependency checking
.\run_windows.ps1

# Or with options
.\run_windows.ps1 -Help                    # Show help
.\run_windows.ps1 -NoCache                 # Force fresh data
.\run_windows.ps1 -SampleSize 1000         # Test with 1000 stars
.\run_windows.ps1 -OutputDir results       # Custom output directory
```

The PowerShell script automatically:
- ✅ Checks Python installation
- ✅ Verifies and installs dependencies
- ✅ Provides helpful error messages
- ✅ Uses Windows-native path separators

### Windows-Specific Notes

- **File Paths**: The application uses Python's `pathlib` which automatically handles Windows path separators
- **Output Location**: Files will be created in the `output\` directory relative to the script location
- **Cache Location**: Cached data is stored in the `data\` directory
- **Progress Bars**: All progress indicators work correctly in PowerShell and Command Prompt
- **Async Operations**: The asynchronous API calls work seamlessly on Windows

### Troubleshooting Windows Issues

**Issue**: `python` command not found
- **Solution**: Ensure Python is installed and added to PATH, or use `py` instead of `python`

**Issue**: PowerShell execution policy prevents script execution
- **Solution**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Issue**: SSL certificate errors
- **Solution**: Update pip and certificates: `python -m pip install --upgrade pip certifi`

**Issue**: Long path names causing issues
- **Solution**: Enable long path support in Windows or use shorter directory names

### Performance on Windows

The application performs well on Windows with typical execution times:
- **Data Collection**: ~2-3 minutes for all New Eden stars
- **Processing**: ~10-30 seconds depending on system specs
- **Visualization**: ~5-15 seconds for all plots

### Example Windows Session

```powershell
PS C:\Users\YourName\Documents> git clone https://github.com/alepmalagon/eve_Hertzsprung_Russell_diagram.git
PS C:\Users\YourName\Documents> cd eve_Hertzsprung_Russell_diagram
PS C:\Users\YourName\Documents\eve_Hertzsprung_Russell_diagram> python -m venv venv
PS C:\Users\YourName\Documents\eve_Hertzsprung_Russell_diagram> .\venv\Scripts\Activate.ps1
(venv) PS C:\Users\YourName\Documents\eve_Hertzsprung_Russell_diagram> pip install -r requirements.txt
(venv) PS C:\Users\YourName\Documents\eve_Hertzsprung_Russell_diagram> python main.py

============================================================
🌟 EVE Online Hertzsprung-Russell Diagram Generator 🌟
============================================================

📡 STEP 1: Collecting Stellar Data
----------------------------------------
🚀 Fetching stellar data from ESI API...
...
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source. EVE Online is a trademark of CCP Games.

## Acknowledgments

- CCP Games for providing the ESI API
- EVE Online community for documentation and support
- Scientific community for H-R diagram conventions and stellar classification systems

## Troubleshooting

### Common Issues

1. **API Rate Limiting**: If you encounter rate limiting errors, the client will automatically retry with backoff
2. **Network Issues**: Check your internet connection and ESI API status
3. **Memory Usage**: For large datasets, consider using the `--sample-size` option for testing
4. **Missing Dependencies**: Ensure all packages in `requirements.txt` are installed

### Logging

The application logs to both console and `eve_hr_diagram.log` file. Check the log file for detailed error information.

## Future Enhancements

- Interactive H-R diagram with plotly
- Stellar evolution track overlays
- Comparison with real astronomical data
- Web interface for easy access
- Additional stellar population analysis
