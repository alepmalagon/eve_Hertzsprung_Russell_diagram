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
import time
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

from src.esi_client import ESIClient
from src.data_processor import StellarDataProcessor
from src.hr_diagram import HRDiagramGenerator
from src.config import get_config, STRATEGIC_SYSTEMS

# Set up logging with UTF-8 encoding to handle Unicode characters
# Configure stdout handler with UTF-8 encoding for Windows compatibility
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setStream(sys.stdout)

# Configure file handler with UTF-8 encoding
file_handler = logging.FileHandler('eve_hr_diagram.log', encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[stdout_handler, file_handler]
)

logger = logging.getLogger(__name__)


async def collect_stellar_data(use_cache: bool = True, cache_file: str = "data/stellar_data.json") -> List[Dict]:
    """Collect stellar data from ESI API or cache"""
    
    cache_path = Path(cache_file)
    
    # Try to load from cache first
    if use_cache and cache_path.exists():
        print("📂 Loading stellar data from cache...")
        with tqdm(desc="Loading cache", unit="MB") as pbar:
            try:
                with open(cache_path, 'r') as f:
                    stellar_data = json.load(f)
                pbar.update(1)
                print(f"✅ Loaded {len(stellar_data):,} stars from cache")
                return stellar_data
            except Exception as e:
                print(f"⚠️  Failed to load cache: {e}. Fetching fresh data...")
    
    # Fetch fresh data from ESI
    print("🚀 Fetching stellar data from ESI API...")
    start_time = time.time()
    
    async with ESIClient() as client:
        # Get all solar systems in New Eden (excluding wormhole space)
        print("🔍 Discovering solar systems in New Eden...")
        system_ids = await client.get_all_systems(exclude_wormhole_regions=True)
        
        if not system_ids:
            print("❌ No solar systems found!")
            return []
            
        print(f"✅ Found {len(system_ids):,} solar systems")
        
        # Get star IDs from systems
        print("⭐ Extracting star IDs from solar systems...")
        star_ids = await client.get_stars_from_systems(system_ids)
        
        if not star_ids:
            print("❌ No stars found!")
            return []
            
        print(f"✅ Found {len(star_ids):,} stars")
        
        # Get stellar data
        print("🌟 Fetching stellar data...")
        stellar_data = await client.get_stellar_data(star_ids)
        
        if not stellar_data:
            print("❌ No stellar data retrieved!")
            return []
            
        elapsed_time = time.time() - start_time
        print(f"✅ Successfully retrieved data for {len(stellar_data):,} stars in {elapsed_time:.1f}s")
    
    # Save to cache
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    print("💾 Saving data to cache...")
    with tqdm(desc="Saving cache", unit="MB") as pbar:
        try:
            with open(cache_path, 'w') as f:
                json.dump(stellar_data, f, indent=2)
            pbar.update(1)
            print(f"✅ Saved stellar data to cache: {cache_file}")
        except Exception as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    return stellar_data


async def collect_strategic_systems_data() -> List[Dict]:
    """Collect stellar data for strategic systems"""
    
    print("🎯 Fetching strategic systems data...")
    start_time = time.time()
    
    async with ESIClient() as client:
        strategic_data = await client.get_strategic_systems_data(STRATEGIC_SYSTEMS)
        
        if not strategic_data:
            print("⚠️  No strategic systems data retrieved!")
            return []
            
        elapsed_time = time.time() - start_time
        print(f"✅ Successfully retrieved data for {len(strategic_data)} strategic systems in {elapsed_time:.1f}s")
        
        # Display which systems were found
        found_systems = [star.get('strategic_system_name', 'Unknown') for star in strategic_data if star.get('strategic_system_name')]
        if found_systems:
            print(f"📍 Strategic systems found: {', '.join(found_systems)}")
        
        missing_systems = set(STRATEGIC_SYSTEMS) - set(found_systems)
        if missing_systems:
            print(f"⚠️  Strategic systems not found: {', '.join(missing_systems)}")
    
    return strategic_data


def process_and_analyze_data(stellar_data: List[Dict]) -> Dict:
    """Process stellar data and generate analysis"""
    
    print("🔬 Processing stellar data...")
    
    # Initialize processor
    processor = StellarDataProcessor()
    
    # Process the data with progress bar
    with tqdm(total=4, desc="Processing steps") as pbar:
        pbar.set_description("🧹 Cleaning data")
        df = processor.process_stellar_data(stellar_data)
        pbar.update(1)
        
        if df.empty:
            print("❌ No valid stellar data after processing!")
            return {}
        
        pbar.set_description("📊 Generating statistics")
        stats = processor.get_summary_statistics(df)
        pbar.update(1)
        
        pbar.set_description("🎯 Filtering for H-R diagram")
        hr_df = processor.filter_for_hr_diagram(df)
        pbar.update(1)
        
        pbar.set_description("✅ Processing complete")
        pbar.update(1)
    
    print(f"✅ Processed {len(df):,} stars ({len(hr_df):,} suitable for H-R diagram)")
    
    # Display key statistics
    if 'spectral_type_distribution' in stats:
        print("📈 Most common spectral types:")
        for spec_type, count in list(stats['spectral_type_distribution'].items())[:5]:
            percentage = count / len(df) * 100
            print(f"   {spec_type}: {count:,} stars ({percentage:.1f}%)")
    
    return {
        'processed_data': df,
        'hr_data': hr_df,
        'statistics': stats
    }


def generate_visualizations(processed_data: Dict, famous_systems: Dict = None, output_dir: str = "output") -> Dict[str, str]:
    """Generate H-R diagram and additional visualizations"""
    
    print("🎨 Generating visualizations...")
    
    hr_data = processed_data['hr_data']
    
    if hr_data.empty:
        print("❌ No data available for H-R diagram!")
        return {}
    
    # Initialize diagram generator
    generator = HRDiagramGenerator()
    
    # Create visualizations with progress tracking
    with tqdm(total=5, desc="Creating plots") as pbar:
        pbar.set_description("📈 Creating H-R diagram")
        hr_diagram_path = generator.create_hr_diagram(hr_data, famous_systems=famous_systems)
        pbar.update(1)
        
        pbar.set_description("📊 Creating analysis plots")
        analysis_plots = generator.create_detailed_analysis(hr_data, output_dir)
        pbar.update(4)  # Analysis creates multiple plots
    
    # Combine all output files
    output_files = {
        'hr_diagram': hr_diagram_path,
        **analysis_plots
    }
    
    print(f"✅ Generated {len(output_files)} visualization files")
    if famous_systems:
        successful_systems = sum(1 for v in famous_systems.values() if v is not None)
        if successful_systems > 0:
            print(f"🌟 Highlighted {successful_systems} famous systems on the H-R diagram")
    
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
    
    # Print header
    print("=" * 60)
    print("🌟 EVE Online Hertzsprung-Russell Diagram Generator 🌟")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    try:
        # Step 1: Collect stellar data
        print("📡 STEP 1: Collecting Stellar Data")
        print("-" * 40)
        stellar_data = await collect_stellar_data(
            use_cache=not args.no_cache,
            cache_file=args.cache_file
        )
        
        if not stellar_data:
            print("❌ No stellar data available. Exiting.")
            return 1
        
        # Limit sample size if requested (for testing)
        if args.sample_size and args.sample_size < len(stellar_data):
            print(f"🔬 Limiting to {args.sample_size:,} stars for testing")
            stellar_data = stellar_data[:args.sample_size]
        
        print()
        
        # Step 1.5: Collect strategic systems data
        print("🎯 STEP 1.5: Collecting Strategic Systems Data")
        print("-" * 40)
        strategic_data = await collect_strategic_systems_data()
        
        # Convert strategic data to famous_systems format for visualization
        famous_systems = {}
        if strategic_data:
            print(f"🔗 Merging {len(strategic_data)} strategic systems with main dataset")
            stellar_data.extend(strategic_data)
            
            # Convert to famous_systems format
            for star_data in strategic_data:
                if 'strategic_system_name' in star_data:
                    system_name = star_data['strategic_system_name']
                    famous_systems[system_name] = {
                        'stellar_data': star_data,
                        'system_name': system_name
                    }
            
            print(f"✅ Prepared {len(famous_systems)} strategic systems for visualization")
        else:
            famous_systems = None
        
        print()
        
        # Step 2: Process and analyze data
        print("🔬 STEP 2: Processing and Analyzing Data")
        print("-" * 40)
        processed_data = process_and_analyze_data(stellar_data)
        
        if not processed_data:
            print("❌ Data processing failed. Exiting.")
            return 1
        
        print()
        
        # Step 4: Generate visualizations
        print("🎨 STEP 4: Generating Visualizations")
        print("-" * 40)
        output_files = generate_visualizations(processed_data, famous_systems, args.output_dir)
        
        if not output_files:
            print("❌ Visualization generation failed. Exiting.")
            return 1
        
        print()
        
        # Step 5: Save results
        print("💾 STEP 5: Saving Results")
        print("-" * 40)
        with tqdm(desc="Saving results", total=2) as pbar:
            save_results(processed_data, output_files, args.output_dir)
            pbar.update(2)
        
        # Success!
        total_time = time.time() - start_time
        print()
        print("🎉 SUCCESS! H-R Diagram generation completed!")
        print("=" * 60)
        print(f"⏱️  Total execution time: {total_time:.1f} seconds")
        print(f"📊 Processed {len(processed_data['processed_data']):,} stars")
        print(f"📈 Generated {len(output_files)} visualization files:")
        
        for name, path in output_files.items():
            print(f"   📄 {name}: {path}")
        
        print()
        print("🌟 Your New Eden Hertzsprung-Russell diagram is ready!")
        print("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
