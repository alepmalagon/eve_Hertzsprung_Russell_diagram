#!/usr/bin/env python3
"""
Debug script to investigate region and system counting issues
"""

import asyncio
import json
from src.esi_client import ESIClient
from src.config import WORMHOLE_REGION_IDS

async def debug_regions():
    """Debug region and system counting"""
    
    async with ESIClient() as client:
        print("🔍 Debugging EVE Online region and system data...")
        print("=" * 60)
        
        # Get all regions
        print("📡 Fetching all regions...")
        all_regions = await client.get_regions()
        print(f"✅ Found {len(all_regions)} total regions")
        
        # Separate k-space and j-space regions
        wormhole_regions = [r for r in all_regions if r in WORMHOLE_REGION_IDS]
        kspace_regions = [r for r in all_regions if r not in WORMHOLE_REGION_IDS]
        
        print(f"📊 K-space regions: {len(kspace_regions)}")
        print(f"📊 J-space regions (by our filter): {len(wormhole_regions)}")
        print(f"📊 Unaccounted regions: {len(all_regions) - len(kspace_regions) - len(wormhole_regions)}")
        
        # Check if there are regions we're not accounting for
        unaccounted = [r for r in all_regions if r not in WORMHOLE_REGION_IDS and r not in kspace_regions]
        if unaccounted:
            print(f"⚠️  Unaccounted region IDs: {unaccounted}")
        
        print("\n🔍 Analyzing region details...")
        
        # Get details for a few regions to understand the pattern
        sample_regions = all_regions[:10]  # Sample first 10 regions
        region_details = []
        
        for region_id in sample_regions:
            region_info = await client.get_region_info(region_id)
            if region_info:
                region_details.append({
                    'id': region_id,
                    'name': region_info.get('name', 'Unknown'),
                    'constellations': len(region_info.get('constellations', [])),
                    'is_wormhole': region_id in WORMHOLE_REGION_IDS
                })
        
        print("\n📋 Sample region details:")
        for region in region_details:
            wh_status = "J-SPACE" if region['is_wormhole'] else "K-SPACE"
            print(f"   {region['id']:8} | {region['name']:20} | {region['constellations']:3} constellations | {wh_status}")
        
        # Now let's count systems in k-space regions
        print(f"\n🌍 Counting systems in {len(kspace_regions)} k-space regions...")
        
        total_systems = 0
        total_stars = 0
        
        # Process regions in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(kspace_regions), batch_size):
            batch = kspace_regions[i:i+batch_size]
            print(f"   Processing regions {i+1}-{min(i+batch_size, len(kspace_regions))} of {len(kspace_regions)}...")
            
            # Get region info for this batch
            region_tasks = []
            for region_id in batch:
                region_tasks.append(client.get_region_info(region_id))
            
            region_results = await asyncio.gather(*region_tasks)
            
            # Count constellations and systems
            batch_constellations = []
            for region_info in region_results:
                if region_info and "constellations" in region_info:
                    batch_constellations.extend(region_info["constellations"])
            
            # Get constellation info
            constellation_tasks = []
            for constellation_id in batch_constellations:
                constellation_tasks.append(client.get_constellation_info(constellation_id))
            
            constellation_results = await asyncio.gather(*constellation_tasks)
            
            # Count systems in this batch
            batch_systems = []
            for constellation_info in constellation_results:
                if constellation_info and "systems" in constellation_info:
                    batch_systems.extend(constellation_info["systems"])
            
            total_systems += len(batch_systems)
            
            # Sample a few systems to count stars
            sample_systems = batch_systems[:min(50, len(batch_systems))]  # Sample up to 50 systems
            system_tasks = []
            for system_id in sample_systems:
                system_tasks.append(client.get_system_info(system_id))
            
            system_results = await asyncio.gather(*system_tasks)
            
            # Count stars in sample
            sample_stars = 0
            for system_info in system_results:
                if system_info and "star_id" in system_info:
                    sample_stars += 1
            
            # Estimate total stars for this batch
            if sample_systems:
                stars_per_system = sample_stars / len(sample_systems)
                estimated_batch_stars = int(len(batch_systems) * stars_per_system)
                total_stars += estimated_batch_stars
                
                print(f"      Batch: {len(batch_systems)} systems, ~{estimated_batch_stars} stars (ratio: {stars_per_system:.2f})")
        
        print("\n📊 FINAL RESULTS:")
        print("=" * 60)
        print(f"🌌 Total regions: {len(all_regions)}")
        print(f"🌍 K-space regions: {len(kspace_regions)}")
        print(f"🕳️  J-space regions (filtered): {len(wormhole_regions)}")
        print(f"🏠 Total k-space systems: {total_systems}")
        print(f"⭐ Estimated k-space stars: {total_stars}")
        print(f"🎯 Expected stars: 5,431")
        print(f"📉 Difference: {5431 - total_stars} stars")
        
        if total_stars < 5431:
            print(f"\n⚠️  We're missing {5431 - total_stars} stars!")
            print("   Possible causes:")
            print("   1. Incomplete wormhole region filtering")
            print("   2. Some k-space regions being incorrectly excluded")
            print("   3. Systems with multiple stars not being counted")
            print("   4. API pagination issues")
        
        # Let's also check if any regions have names starting with 'J'
        print(f"\n🔍 Checking for J-named regions...")
        j_regions = []
        for region_id in all_regions[:20]:  # Check first 20 regions
            region_info = await client.get_region_info(region_id)
            if region_info and region_info.get('name', '').startswith('J'):
                j_regions.append((region_id, region_info['name']))
        
        if j_regions:
            print("   Found J-named regions:")
            for region_id, name in j_regions:
                in_filter = region_id in WORMHOLE_REGION_IDS
                print(f"      {region_id}: {name} {'(filtered)' if in_filter else '(NOT filtered!)'}")
        else:
            print("   No J-named regions found in sample")

if __name__ == "__main__":
    asyncio.run(debug_regions())
