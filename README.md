# EVE Online New Eden Hertzsprung-Russell Diagram Generator

This project generates a Hertzsprung-Russell (H-R) diagram for all stars in the New Eden cluster from EVE Online, using data from the ESI (EVE Swagger Interface) API.

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

1. Clone the repository:
```bash
git clone https://github.com/alepmalagon/eve_Hertzsprung_Russell_diagram.git
cd eve_Hertzsprung_Russell_diagram
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate the H-R diagram with default settings:
```bash
python main.py
```

### Advanced Options

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
