"""
ESI API Client for EVE Online data fetching
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from asyncio_throttle import Throttler
from tqdm.asyncio import tqdm

from .config import (
    ESI_BASE_URL, ESI_DATASOURCE, ESI_VERSION, ESI_RATE_LIMIT,
    USER_AGENT, REQUEST_TIMEOUT
)

logger = logging.getLogger(__name__)


class ESIClient:
    """Asynchronous ESI API client with rate limiting and error handling"""
    
    def __init__(self):
        self.base_url = ESI_BASE_URL
        self.datasource = ESI_DATASOURCE
        self.version = ESI_VERSION
        self.user_agent = USER_AGENT
        self.timeout = REQUEST_TIMEOUT
        self.throttler = Throttler(rate_limit=ESI_RATE_LIMIT, period=1.0)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={"User-Agent": self.user_agent}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a rate-limited request to the ESI API"""
        if not self.session:
            raise RuntimeError("ESI client not initialized. Use async context manager.")
            
        url = f"{self.base_url}/{self.version}/{endpoint}"
        
        # Default parameters
        request_params = {
            "datasource": self.datasource,
        }
        if params:
            request_params.update(params)
            
        async with self.throttler:
            try:
                async with self.session.get(url, params=request_params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"Resource not found: {url}")
                        return None
                    elif response.status == 420:  # Error limited
                        logger.error("ESI error limit reached")
                        await asyncio.sleep(60)  # Wait a minute before retrying
                        return await self._make_request(endpoint, params)
                    else:
                        logger.error(f"ESI request failed: {response.status} - {url}")
                        return None
                        
            except asyncio.TimeoutError:
                logger.error(f"Request timeout: {url}")
                return None
            except Exception as e:
                logger.error(f"Request error: {e} - {url}")
                return None
                
    async def get_regions(self) -> List[int]:
        """Get all region IDs"""
        data = await self._make_request("universe/regions/")
        return data if data else []
        
    async def get_region_info(self, region_id: int) -> Optional[Dict]:
        """Get information about a specific region"""
        return await self._make_request(f"universe/regions/{region_id}/")
        
    async def get_systems_in_region(self, region_id: int) -> List[int]:
        """Get all system IDs in a region"""
        region_info = await self.get_region_info(region_id)
        return region_info.get("constellations", []) if region_info else []
        
    async def get_constellation_info(self, constellation_id: int) -> Optional[Dict]:
        """Get information about a constellation"""
        return await self._make_request(f"universe/constellations/{constellation_id}/")
        
    async def get_system_info(self, system_id: int) -> Optional[Dict]:
        """Get information about a solar system"""
        return await self._make_request(f"universe/systems/{system_id}/")
        
    async def get_star_info(self, star_id: int) -> Optional[Dict]:
        """Get stellar data for a specific star"""
        return await self._make_request(f"universe/stars/{star_id}/")
        
    async def get_all_systems(self, exclude_wormhole_regions: bool = True) -> List[int]:
        """Get all solar system IDs, optionally excluding wormhole space"""
        from .config import WORMHOLE_REGION_IDS
        
        logger.info("Fetching all regions...")
        regions = await self.get_regions()
        
        if exclude_wormhole_regions:
            regions = [r for r in regions if r not in WORMHOLE_REGION_IDS]
            logger.info(f"Excluding {len(WORMHOLE_REGION_IDS)} wormhole regions")
            
        logger.info(f"Processing {len(regions)} regions...")
        
        all_systems = []
        
        # Get all constellations from all regions
        constellation_tasks = []
        for region_id in regions:
            constellation_tasks.append(self.get_region_info(region_id))
            
        region_results = await tqdm.gather(*constellation_tasks, desc="Fetching regions")
        
        # Collect all constellation IDs
        constellation_ids = []
        for region_info in region_results:
            if region_info and "constellations" in region_info:
                constellation_ids.extend(region_info["constellations"])
                
        logger.info(f"Found {len(constellation_ids)} constellations")
        
        # Get all systems from all constellations
        constellation_tasks = []
        for constellation_id in constellation_ids:
            constellation_tasks.append(self.get_constellation_info(constellation_id))
            
        constellation_results = await tqdm.gather(*constellation_tasks, desc="Fetching constellations")
        
        # Collect all system IDs
        for constellation_info in constellation_results:
            if constellation_info and "systems" in constellation_info:
                all_systems.extend(constellation_info["systems"])
                
        logger.info(f"Found {len(all_systems)} solar systems in New Eden")
        return all_systems
        
    async def get_stars_from_systems(self, system_ids: List[int]) -> List[int]:
        """Get all star IDs from a list of solar systems"""
        logger.info(f"Fetching star IDs from {len(system_ids)} systems...")
        
        system_tasks = []
        for system_id in system_ids:
            system_tasks.append(self.get_system_info(system_id))
            
        system_results = await tqdm.gather(*system_tasks, desc="Fetching systems")
        
        star_ids = []
        for system_info in system_results:
            if system_info and "star_id" in system_info:
                star_ids.append(system_info["star_id"])
                
        logger.info(f"Found {len(star_ids)} stars")
        return star_ids
        
    async def get_stellar_data(self, star_ids: List[int]) -> List[Dict]:
        """Get stellar data for multiple stars"""
        logger.info(f"Fetching stellar data for {len(star_ids)} stars...")
        
        star_tasks = []
        for star_id in star_ids:
            star_tasks.append(self.get_star_info(star_id))
            
        star_results = await tqdm.gather(*star_tasks, desc="Fetching stellar data")
        
        # Filter out None results
        stellar_data = [star for star in star_results if star is not None]
        
        logger.info(f"Successfully fetched data for {len(stellar_data)} stars")
        return stellar_data
