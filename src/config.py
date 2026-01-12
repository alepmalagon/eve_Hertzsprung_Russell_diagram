"""
Configuration settings for the EVE H-R Diagram Generator
"""

import os
from typing import Dict, Any

# ESI API Configuration
ESI_BASE_URL = "https://esi.evetech.net"
ESI_DATASOURCE = "tranquility"
ESI_VERSION = "latest"

# API Rate limiting (requests per second)
ESI_RATE_LIMIT = 150  # ESI allows 150 requests per second

# User Agent for ESI requests (required by ESI)
USER_AGENT = "EVE-HR-Diagram-Generator/1.0.0 (https://github.com/alepmalagon/eve_Hertzsprung_Russell_diagram)"

# Request timeout settings
REQUEST_TIMEOUT = 30  # seconds

# Data file paths
DATA_DIR = "data"
OUTPUT_DIR = "output"

# Known wormhole space region IDs (Aniokis galaxy)
# These are the region IDs for wormhole space that should be excluded
WORMHOLE_REGION_IDS = {
    11000001,  # A-R00001
    11000002,  # A-R00002  
    11000003,  # A-R00003
    11000004,  # B-R00004
    11000005,  # B-R00005
    11000006,  # B-R00006
    11000007,  # B-R00007
    11000008,  # B-R00008
    11000009,  # C-R00009
    11000010,  # C-R00010
    11000011,  # C-R00011
    11000012,  # C-R00012
    11000013,  # C-R00013
    11000014,  # C-R00014
    11000015,  # C-R00015
    11000016,  # C-R00016
    11000017,  # C-R00017
    11000018,  # C-R00018
    11000019,  # C-R00019
    11000020,  # C-R00020
    11000021,  # C-R00021
    11000022,  # C-R00022
    11000023,  # C-R00023
    11000024,  # C-R00024
    11000025,  # C-R00025
    11000026,  # C-R00026
    11000027,  # C-R00027
    11000028,  # C-R00028
    11000029,  # C-R00029
    11000030,  # C-R00030
    11000031,  # C-R00031
}

# Strategic Systems Configuration
# These are important systems in EVE Online that should be highlighted on the HR diagram
STRATEGIC_SYSTEMS = [
    "Auga",      # Minmatar/Amarr border system
    "Amamake",   # Low-sec PvP hotspot
    "Ahbazon",   # Amarr region system
    "Tama",      # Famous PvP system
    "Jita",      # Major trade hub
    "Amarr",     # Amarr Empire capital
    "Sosala",    # Amarr region system
    "Vard",      # Minmatar region system
    "Dodixie",   # Gallente trade hub
    "Rens",      # Minmatar trade hub
    "Hek",       # Minmatar trade hub
    "1DQ1-A",    # Goonswarm Federation capital
    "R-6KYM",    # Null-sec system
    "Udema",     # High-sec system
    "Rancer",    # Low-sec PvP system
    "Mehatoor",  # Amarr region system
]

# H-R Diagram configuration
HR_DIAGRAM_CONFIG = {
    "figsize": (12, 8),
    "dpi": 300,
    "title": "Hertzsprung-Russell Diagram - New Eden Cluster",
    "xlabel": "Temperature (K)",
    "ylabel": "Luminosity (Solar Luminosities)",
    "log_scale_y": True,
    "invert_x": True,  # H-R diagrams traditionally have temperature decreasing left to right
    "alpha": 0.6,
    "marker_size": 20,
    # Strategic systems highlighting configuration
    "strategic_marker_size": 80,
    "strategic_alpha": 0.9,
    "strategic_color": "#FF6B6B",  # Bright red for visibility
    "strategic_edge_color": "#000000",  # Black border
    "strategic_edge_width": 2,
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary"""
    return {
        "esi_base_url": ESI_BASE_URL,
        "esi_datasource": ESI_DATASOURCE,
        "esi_version": ESI_VERSION,
        "esi_rate_limit": ESI_RATE_LIMIT,
        "user_agent": USER_AGENT,
        "request_timeout": REQUEST_TIMEOUT,
        "data_dir": DATA_DIR,
        "output_dir": OUTPUT_DIR,
        "wormhole_region_ids": WORMHOLE_REGION_IDS,
        "strategic_systems": STRATEGIC_SYSTEMS,
        "hr_diagram_config": HR_DIAGRAM_CONFIG,
    }
