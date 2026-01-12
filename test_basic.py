#!/usr/bin/env python3
"""
Basic test script to verify the EVE H-R Diagram Generator functionality
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from esi_client import ESIClient
from data_processor import StellarDataProcessor
from hr_diagram import HRDiagramGenerator
from config import get_config

async def test_esi_client():
    """Test basic ESI client functionality"""
    print("Testing ESI Client...")
    
    async with ESIClient() as client:
        # Test getting regions
        regions = await client.get_regions()
        print(f"Found {len(regions)} regions")
        
        if regions:
            # Test getting region info
            region_info = await client.get_region_info(regions[0])
            print(f"First region info: {region_info}")
            
            # Test getting a few systems (limit for testing)
            system_ids = await client.get_all_systems()
            print(f"Found {len(system_ids)} systems in New Eden")
            
            if system_ids:
                # Test getting star IDs from a few systems
                test_systems = system_ids[:5]  # Just test first 5
                star_ids = await client.get_stars_from_systems(test_systems)
                print(f"Found {len(star_ids)} stars in first 5 systems")
                
                if star_ids:
                    # Test getting stellar data for a few stars
                    test_stars = star_ids[:3]  # Just test first 3
                    stellar_data = await client.get_stellar_data(test_stars)
                    print(f"Retrieved data for {len(stellar_data)} stars")
                    
                    if stellar_data:
                        print("Sample stellar data:")
                        for star in stellar_data:
                            print(f"  {star}")
                    
                    return stellar_data
    
    return []

def test_data_processor(stellar_data):
    """Test data processing functionality"""
    print("\nTesting Data Processor...")
    
    if not stellar_data:
        print("No stellar data to process")
        return None
    
    processor = StellarDataProcessor()
    df = processor.process_stellar_data(stellar_data)
    
    print(f"Processed DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    if not df.empty:
        stats = processor.get_summary_statistics(df)
        print("Summary statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        hr_df = processor.filter_for_hr_diagram(df)
        print(f"H-R diagram data shape: {hr_df.shape}")
        
        return {'processed_data': df, 'hr_data': hr_df, 'statistics': stats}
    
    return None

def test_hr_diagram(processed_data):
    """Test H-R diagram generation"""
    print("\nTesting H-R Diagram Generator...")
    
    if not processed_data or processed_data['hr_data'].empty:
        print("No data available for H-R diagram")
        return
    
    generator = HRDiagramGenerator()
    
    # Create test output directory
    Path("test_output").mkdir(exist_ok=True)
    
    try:
        hr_path = generator.create_hr_diagram(
            processed_data['hr_data'], 
            "test_output/test_hr_diagram.png"
        )
        print(f"H-R diagram saved to: {hr_path}")
        
        # Test additional analysis
        analysis_plots = generator.create_detailed_analysis(
            processed_data['hr_data'], 
            "test_output"
        )
        print(f"Additional plots: {list(analysis_plots.keys())}")
        
    except Exception as e:
        print(f"Error generating H-R diagram: {e}")

async def main():
    """Run basic tests"""
    print("EVE H-R Diagram Generator - Basic Test")
    print("=" * 50)
    
    # Test configuration
    config = get_config()
    print(f"Configuration loaded: {len(config)} settings")
    
    # Test ESI client
    stellar_data = await test_esi_client()
    
    # Test data processor
    processed_data = test_data_processor(stellar_data)
    
    # Test H-R diagram generator
    test_hr_diagram(processed_data)
    
    print("\nBasic test completed!")

if __name__ == "__main__":
    asyncio.run(main())
