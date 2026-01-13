#!/usr/bin/env python3
"""
Quick test to verify the famous_systems fix works
"""

import sys
import asyncio
from unittest.mock import patch, AsyncMock

# Mock the ESI client to avoid API calls
async def mock_collect_stellar_data(*args, **kwargs):
    return [
        {
            'type_id': 3802,
            'temperature': 5778,
            'luminosity': 1.0,
            'solar_system_id': 30000142,
            'name': 'Test Star'
        }
    ]

async def mock_collect_strategic_systems_data():
    return [
        {
            'type_id': 3802,
            'temperature': 6000,
            'luminosity': 1.2,
            'solar_system_id': 30000142,
            'strategic_system_name': 'Jita',
            'is_strategic': True
        }
    ]

def mock_process_and_analyze_data(stellar_data):
    import pandas as pd
    df = pd.DataFrame(stellar_data)
    return {
        'processed_data': df,
        'hr_data': df,
        'statistics': {'total_stars': len(df)}
    }

def mock_generate_visualizations(processed_data, famous_systems, output_dir):
    print(f"✅ Mock visualization called with famous_systems: {famous_systems}")
    return {'hr_diagram': 'test_output.png'}

def mock_save_results(processed_data, output_files, output_dir):
    print("✅ Mock save results called")

# Patch the functions to avoid actual API calls and file operations
async def test_main():
    with patch('main.collect_stellar_data', mock_collect_stellar_data), \
         patch('main.collect_strategic_systems_data', mock_collect_strategic_systems_data), \
         patch('main.process_and_analyze_data', mock_process_and_analyze_data), \
         patch('main.generate_visualizations', mock_generate_visualizations), \
         patch('main.save_results', mock_save_results):
        
        # Import main after patching
        import main
        
        # Mock sys.argv to simulate command line args
        original_argv = sys.argv
        sys.argv = ['main.py', '--sample-size', '1']
        
        try:
            result = await main.main()
            print(f"✅ Script completed successfully with exit code: {result}")
            return result
        except Exception as e:
            print(f"❌ Script failed with error: {e}")
            return 1
        finally:
            sys.argv = original_argv

if __name__ == "__main__":
    exit_code = asyncio.run(test_main())
    print(f"Test completed with exit code: {exit_code}")
