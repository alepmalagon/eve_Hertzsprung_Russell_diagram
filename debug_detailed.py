#!/usr/bin/env python3
"""
Detailed debug script to find exactly where we're losing stars
"""

import asyncio
import json
from src.esi_client import ESIClient
from src.config import WORMHOLE_REGION_IDS

async def debug_detailed():
    """Detailed debugging to find missing stars"""
    
    async with ESIClient() as client:
        print("🔍 DETAILED DEBUGGING - Finding Missing Stars")
        print("=" * 60)
        
        # Step 1: Get all systems using the current logic
        print("📡 Step 1: Getting all k-space systems using current logic...")
        systems = await client.get_all_systems(exclude_wormhole_regions=True)
        print(f"✅ Found {len(systems)} k-space systems")
        
        # Step 2: Get star IDs from systems
        print(f"\n⭐ Step 2: Extracting star IDs from {len(systems)} systems...")
        star_ids = await client.get_stars_from_systems(systems)
        print(f"✅ Found {len(star_ids)} star IDs")
        
        if len(star_ids) != len(systems):
            missing_stars = len(systems) - len(star_ids)
            print(f"⚠️  WARNING: {missing_stars} systems don't have star_id!")
        
        # Step 3: Sample some systems to check for missing star_id
        print(f"\n🔍 Step 3: Checking sample systems for missing star_id...")
        sample_size = min(100, len(systems))
        sample_systems = systems[:sample_size]
        
        systems_without_stars = 0
        systems_with_stars = 0
        
        for i, system_id in enumerate(sample_systems):
            system_info = await client.get_system_info(system_id)
            if system_info:
                if "star_id" in system_info:
                    systems_with_stars += 1
                else:
                    systems_without_stars += 1
                    print(f"   System {system_id} ({system_info.get('name', 'Unknown')}) has NO star_id")
            else:
                print(f"   System {system_id} returned NO data")
            
            if i % 20 == 0:
                print(f"   Checked {i+1}/{sample_size} systems...")
        
        print(f"📊 Sample results: {systems_with_stars} with stars, {systems_without_stars} without stars")
        
        # Step 4: Try to fetch stellar data for the star IDs we found
        print(f"\n🌟 Step 4: Fetching stellar data for {len(star_ids)} stars...")
        stellar_data = await client.get_stellar_data(star_ids)
        print(f"✅ Successfully fetched data for {len(stellar_data)} stars")
        
        if len(stellar_data) != len(star_ids):
            missing_stellar_data = len(star_ids) - len(stellar_data)
            print(f"⚠️  WARNING: {missing_stellar_data} stars returned no data!")
        
        # Step 5: Check what stellar data we're getting
        print(f"\n📋 Step 5: Analyzing stellar data quality...")
        valid_stars = 0
        invalid_stars = 0
        missing_fields = {
            'luminosity': 0,
            'temperature': 0,
            'spectral_class': 0,
            'radius': 0,
            'age': 0,
            'name': 0
        }
        
        sample_stellar_data = stellar_data[:min(50, len(stellar_data))]
        
        for star_data in sample_stellar_data:
            if star_data:
                valid_stars += 1
                # Check for missing fields
                for field in missing_fields.keys():
                    if field not in star_data or star_data[field] is None:
                        missing_fields[field] += 1
            else:
                invalid_stars += 1
        
        print(f"📊 Stellar data quality (sample of {len(sample_stellar_data)}):")
        print(f"   Valid stars: {valid_stars}")
        print(f"   Invalid/null stars: {invalid_stars}")
        print(f"   Missing fields:")
        for field, count in missing_fields.items():
            if count > 0:
                percentage = (count / len(sample_stellar_data)) * 100
                print(f"     {field}: {count} missing ({percentage:.1f}%)")
        
        # Step 6: Check if we're filtering out j-space systems correctly
        print(f"\n🕳️  Step 6: Checking j-space system filtering...")
        
        # Get a few systems and check their names
        sample_systems_info = []
        for system_id in systems[:20]:
            system_info = await client.get_system_info(system_id)
            if system_info:
                sample_systems_info.append({
                    'id': system_id,
                    'name': system_info.get('name', 'Unknown'),
                    'has_star': 'star_id' in system_info
                })
        
        j_named_systems = [s for s in sample_systems_info if s['name'].startswith('J') and s['name'][1:2].isdigit()]
        
        if j_named_systems:
            print(f"⚠️  Found {len(j_named_systems)} J-space systems that weren't filtered:")
            for sys in j_named_systems:
                print(f"     {sys['id']}: {sys['name']} (has_star: {sys['has_star']})")
        else:
            print("✅ No J-space systems found in sample - filtering appears correct")
        
        # Step 7: Final summary
        print(f"\n📊 FINAL ANALYSIS:")
        print("=" * 60)
        print(f"🌍 K-space systems found: {len(systems)}")
        print(f"⭐ Star IDs extracted: {len(star_ids)}")
        print(f"🌟 Stellar data fetched: {len(stellar_data)}")
        print(f"🎯 Expected stars: 5,431")
        print(f"📉 Current shortfall: {5431 - len(stellar_data)} stars")
        
        # Calculate where we're losing stars
        system_to_star_loss = len(systems) - len(star_ids)
        star_to_data_loss = len(star_ids) - len(stellar_data)
        
        print(f"\n🔍 Loss Analysis:")
        print(f"   Systems without star_id: {system_to_star_loss}")
        print(f"   Stars without data: {star_to_data_loss}")
        print(f"   Total systems vs expected: {len(systems)} vs ~5,431")
        
        if len(systems) < 5431:
            print(f"   ⚠️  We're missing {5431 - len(systems)} systems entirely!")
            print(f"   This suggests our region filtering is too aggressive")
        
        return {
            'systems_found': len(systems),
            'star_ids_found': len(star_ids),
            'stellar_data_found': len(stellar_data),
            'system_to_star_loss': system_to_star_loss,
            'star_to_data_loss': star_to_data_loss
        }

if __name__ == "__main__":
    results = asyncio.run(debug_detailed())
    print(f"\n🎯 Debug completed. Results: {results}")
