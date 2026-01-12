#!/usr/bin/env python3
"""
EVE Online Hertzsprung-Russell Diagram Generator

This script generates H-R diagrams for stars in the New Eden cluster
using data from the EVE Online ESI API.
"""

import asyncio
import json
import logging
import argparse
import sys
from pathlib import Path
from typing import Dict, List

from src.esi_client import ESIClient
from src.data_processor import StellarDataProcessor
from src.hr_diagram import HRDiagramGenerator
from src.config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('eve_hr_diagram.log')
    ]
)

logger = logging.getLogger(__name__)


async def collect_stellar_data(use_cache: bool = True, cache_file: str = "data/stellar_data.json") -> List[Dict]:
    """Collect stellar data from ESI API or cache"""
    
    cache_path = Path(cache_file)
    
    # Try to load from cache first
    if use_cache and cache_path.exists():
        logger.info(f"Loading stellar data from cache: {cache_file}")
        try:
            with open(cache_path, 'r') as f:
                stellar_data = json.load(f)
            logger.info(f"Loaded {len(stellar_data)} stars from cache")
            return stellar_data
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}. Fetching fresh data...")
    
    # Fetch fresh data from ESI
    logger.info("Fetching stellar data from ESI API...")
    
    async with ESIClient() as client:
        # Get all solar systems in New Eden (excluding wormhole space)
        logger.info("Discovering solar systems in New Eden...")
        system_ids = await client.get_all_systems(exclude_wormhole_regions=True)
        
        if not system_ids:
            logger.error("No solar systems found!")
            return []
            
        logger.info(f"Found {len(system_ids)} solar systems")
        
        # Get star IDs from systems
        logger.info("Extracting star IDs from solar systems...")
        star_ids = await client.get_stars_from_systems(system_ids)
        
        if not star_ids:
            logger.error("No stars found!")
            return []
            
        logger.info(f"Found {len(star_ids)} stars")
        
        # Get stellar data
        logger.info("Fetching stellar data...")
        stellar_data = await client.get_stellar_data(star_ids)
        
        if not stellar_data:
            logger.error("No stellar data retrieved!")
            return []
            
        logger.info(f"Successfully retrieved data for {len(stellar_data)} stars")
    
    # Save to cache
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_path, 'w') as f:
            json.dump(stellar_data, f, indent=2)
        logger.info(f"Saved stellar data to cache: {cache_file}")
    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")
    
    return stellar_data


def process_and_analyze_data(stellar_data: List[Dict]) -> Dict:
    """Process stellar data and generate analysis"""
    
    logger.info("Processing stellar data...")
    
    # Initialize processor
    processor = StellarDataProcessor()
    
    # Process the data
    df = processor.process_stellar_data(stellar_data)
    
    if df.empty:
        logger.error("No valid stellar data after processing!")
        return {}
    
    # Generate summary statistics
    stats = processor.get_summary_statistics(df)
    logger.info("Summary statistics:")
    for key, value in stats.items():
        if isinstance(value, dict):
            logger.info(f"  {key}:")
            for subkey, subvalue in value.items():
                logger.info(f"    {subkey}: {subvalue}")
        else:
            logger.info(f"  {key}: {value}")
    
    # Filter for H-R diagram
    hr_df = processor.filter_for_hr_diagram(df)
    
    return {
        'processed_data': df,
        'hr_data': hr_df,
        'statistics': stats
    }


def generate_visualizations(processed_data: Dict, output_dir: str = "output") -> Dict[str, str]:
    """Generate H-R diagram and additional visualizations"""
    
    logger.info("Generating visualizations...")
    
    hr_data = processed_data['hr_data']
    
    if hr_data.empty:
        logger.error("No data available for H-R diagram!")
        return {}
    
    # Initialize diagram generator
    generator = HRDiagramGenerator()
    
    # Create main H-R diagram
    hr_diagram_path = generator.create_hr_diagram(hr_data)
    
    # Create additional analysis plots
    analysis_plots = generator.create_detailed_analysis(hr_data, output_dir)
    
    # Combine all output files
    output_files = {
        'hr_diagram': hr_diagram_path,
        **analysis_plots
    }
    
    return output_files


def save_results(processed_data: Dict, output_files: Dict[str, str], output_dir: str = "output"):
    """Save processed data and results summary"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save processed data
    processed_data_file = output_path / "processed_stellar_data.json"
    try:
        # Convert DataFrame to dict for JSON serialization
        data_to_save = {
            'statistics': processed_data['statistics'],
            'total_stars': len(processed_data['processed_data']),
            'hr_diagram_stars': len(processed_data['hr_data']),
            'columns': list(processed_data['processed_data'].columns)
        }
        
        with open(processed_data_file, 'w') as f:
            json.dump(data_to_save, f, indent=2, default=str)
        
        logger.info(f"Saved processed data summary to: {processed_data_file}")
    except Exception as e:
        logger.warning(f"Failed to save processed data: {e}")
    
    # Save results summary
    summary_file = output_path / "results_summary.txt"
    try:
        with open(summary_file, 'w') as f:
            f.write("EVE Online New Eden Cluster - Hertzsprung-Russell Diagram\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Total stars processed: {len(processed_data['processed_data'])}\n")
            f.write(f"Stars in H-R diagram: {len(processed_data['hr_data'])}\n\n")
            
            f.write("Generated files:\n")
            for name, path in output_files.items():
                f.write(f"  {name}: {path}\n")
            
            f.write("\nStatistics:\n")
            stats = processed_data['statistics']
            
            if 'spectral_type_distribution' in stats:
                f.write("\nSpectral Type Distribution:\n")
                for spec_type, count in stats['spectral_type_distribution'].items():
                    percentage = count / len(processed_data['processed_data']) * 100
                    f.write(f"  {spec_type}: {count} ({percentage:.1f}%)\n")
            
            if 'temperature' in stats:
                temp_stats = stats['temperature']
                f.write(f"\nTemperature Range: {temp_stats['min']:.0f}K - {temp_stats['max']:.0f}K\n")
                f.write(f"Average Temperature: {temp_stats['mean']:.0f}K\n")
            
            if 'luminosity' in stats:
                lum_stats = stats['luminosity']
                f.write(f"\nLuminosity Range: {lum_stats['min']:.2e} - {lum_stats['max']:.2e} L☉\n")
                f.write(f"Average Luminosity: {lum_stats['mean']:.2e} L☉\n")
        
        logger.info(f"Saved results summary to: {summary_file}")
    except Exception as e:
        logger.warning(f"Failed to save results summary: {e}")


async def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="Generate H-R diagram for EVE Online New Eden cluster")
    parser.add_argument("--no-cache", action="store_true", help="Force fresh data fetch (ignore cache)")
    parser.add_argument("--cache-file", default="data/stellar_data.json", help="Cache file path")
    parser.add_argument("--output-dir", default="output", help="Output directory for results")
    parser.add_argument("--sample-size", type=int, help="Limit to N stars for testing")
    
    args = parser.parse_args()
    
    logger.info("Starting EVE Online H-R Diagram Generation")
    logger.info(f"Configuration: {get_config()}")
    
    try:
        # Step 1: Collect stellar data
        stellar_data = await collect_stellar_data(
            use_cache=not args.no_cache,
            cache_file=args.cache_file
        )
        
        if not stellar_data:
            logger.error("No stellar data available. Exiting.")
            return 1
        
        # Limit sample size if requested (for testing)
        if args.sample_size and args.sample_size < len(stellar_data):
            logger.info(f"Limiting to {args.sample_size} stars for testing")
            stellar_data = stellar_data[:args.sample_size]
        
        # Step 2: Process and analyze data
        processed_data = process_and_analyze_data(stellar_data)
        
        if not processed_data:
            logger.error("Data processing failed. Exiting.")
            return 1
        
        # Step 3: Generate visualizations
        output_files = generate_visualizations(processed_data, args.output_dir)
        
        if not output_files:
            logger.error("Visualization generation failed. Exiting.")
            return 1
        
        # Step 4: Save results
        save_results(processed_data, output_files, args.output_dir)
        
        # Success!
        logger.info("H-R Diagram generation completed successfully!")
        logger.info("Generated files:")
        for name, path in output_files.items():
            logger.info(f"  {name}: {path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
