"""
Data processing utilities for stellar data
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm

logger = logging.getLogger(__name__)


class StellarDataProcessor:
    """Process and clean stellar data for H-R diagram generation"""
    
    def __init__(self):
        self.spectral_class_order = {
            'O': 0, 'B': 1, 'A': 2, 'F': 3, 'G': 4, 'K': 5, 'M': 6,
            'L': 7, 'T': 8, 'Y': 9  # Brown dwarf classes
        }
        
    def process_stellar_data(self, stellar_data: List[Dict]) -> pd.DataFrame:
        """Process raw stellar data into a clean DataFrame"""
        
        # Convert to DataFrame
        df = pd.DataFrame(stellar_data)
        
        # Clean and validate data
        df = self._clean_data(df)
        df = self._add_derived_columns(df)
        
        return df
        
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate stellar data"""
        initial_count = len(df)
        logger.info(f"Starting data cleaning with {initial_count} stars")
        
        # Remove rows with missing critical data
        critical_columns = ['luminosity', 'temperature', 'spectral_class']
        for col in critical_columns:
            if col in df.columns:
                before_count = len(df)
                df = df.dropna(subset=[col])
                after_count = len(df)
                if before_count != after_count:
                    logger.info(f"   Removed {before_count - after_count} stars missing {col}")
                
        # Remove invalid values
        if 'luminosity' in df.columns:
            before_count = len(df)
            df = df[df['luminosity'] > 0]  # Luminosity must be positive
            after_count = len(df)
            if before_count != after_count:
                logger.info(f"   Removed {before_count - after_count} stars with non-positive luminosity")
            
        if 'temperature' in df.columns:
            before_count = len(df)
            df = df[df['temperature'] > 0]  # Temperature must be positive
            after_count = len(df)
            if before_count != after_count:
                logger.info(f"   Removed {before_count - after_count} stars with non-positive temperature")
                
            before_count = len(df)
            df = df[df['temperature'] < 100000]  # Reasonable upper limit
            after_count = len(df)
            if before_count != after_count:
                logger.info(f"   Removed {before_count - after_count} stars with temperature > 100,000K")
            
        if 'radius' in df.columns:
            before_count = len(df)
            df = df[df['radius'] > 0]  # Radius must be positive
            after_count = len(df)
            if before_count != after_count:
                logger.info(f"   Removed {before_count - after_count} stars with non-positive radius")
            
        if 'age' in df.columns:
            before_count = len(df)
            df = df[df['age'] >= 0]  # Age must be non-negative
            after_count = len(df)
            if before_count != after_count:
                logger.info(f"   Removed {before_count - after_count} stars with negative age")
            
        # REMOVED: Overly aggressive 3-sigma outlier removal
        # This was incorrectly removing legitimate stellar data like supergiants and red dwarfs
        # Stellar luminosity and temperature naturally span many orders of magnitude
        
        # Instead, only remove truly extreme/impossible values
        if 'luminosity' in df.columns:
            before_count = len(df)
            # Remove stars with luminosity > 10^6 solar luminosities (extremely rare hypergiants)
            df = df[df['luminosity'] <= 1000000]
            # Remove stars with luminosity < 10^-6 solar luminosities (below brown dwarf limit)
            df = df[df['luminosity'] >= 0.000001]
            after_count = len(df)
            if before_count != after_count:
                logger.info(f"   Removed {before_count - after_count} stars with extreme luminosity values")
                
        if 'temperature' in df.columns:
            before_count = len(df)
            # Remove stars with temperature < 500K (too cold for any star)
            df = df[df['temperature'] >= 500]
            # Temperature upper limit already applied above (100,000K)
            after_count = len(df)
            if before_count != after_count:
                logger.info(f"   Removed {before_count - after_count} stars with temperature < 500K")
                
        cleaned_count = len(df)
        removed_count = initial_count - cleaned_count
        
        logger.info(f"Data cleaning complete: removed {removed_count} invalid records ({removed_count/initial_count*100:.1f}%)")
        logger.info(f"Remaining records: {cleaned_count}")
        
        return df
        
    def _add_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived columns for analysis"""
        
        # Parse spectral class
        if 'spectral_class' in df.columns:
            df['spectral_type'] = df['spectral_class'].apply(self._parse_spectral_type)
            df['spectral_subclass'] = df['spectral_class'].apply(self._parse_spectral_subclass)
            df['luminosity_class'] = df['spectral_class'].apply(self._parse_luminosity_class)
            df['spectral_order'] = df['spectral_type'].map(self.spectral_class_order)
            
        # Calculate absolute magnitude from luminosity
        if 'luminosity' in df.columns:
            # M = M_sun - 2.5 * log10(L/L_sun)
            # Where M_sun = 4.83 (absolute magnitude of the Sun)
            df['absolute_magnitude'] = 4.83 - 2.5 * np.log10(df['luminosity'])
            
        # Calculate color index approximation from temperature
        if 'temperature' in df.columns:
            # Rough B-V color index approximation
            df['color_index_bv'] = self._temperature_to_color_index(df['temperature'])
            
        # Calculate stellar mass estimate (very rough approximation)
        if 'luminosity' in df.columns and 'temperature' in df.columns:
            df['estimated_mass'] = self._estimate_stellar_mass(df['luminosity'], df['temperature'])
            
        return df
        
    def _parse_spectral_type(self, spectral_class: str) -> str:
        """Extract the main spectral type (O, B, A, F, G, K, M, etc.)"""
        if pd.isna(spectral_class) or not spectral_class:
            return 'Unknown'
        
        spectral_class = str(spectral_class).strip().upper()
        
        # Extract the first letter
        for char in spectral_class:
            if char in self.spectral_class_order:
                return char
                
        return 'Unknown'
        
    def _parse_spectral_subclass(self, spectral_class: str) -> Optional[int]:
        """Extract the spectral subclass number (0-9)"""
        if pd.isna(spectral_class) or not spectral_class:
            return None
            
        spectral_class = str(spectral_class).strip()
        
        # Look for digits after the spectral type
        for i, char in enumerate(spectral_class):
            if char.isdigit():
                return int(char)
                
        return None
        
    def _parse_luminosity_class(self, spectral_class: str) -> str:
        """Extract the luminosity class (I, II, III, IV, V, etc.)"""
        if pd.isna(spectral_class) or not spectral_class:
            return 'Unknown'
            
        spectral_class = str(spectral_class).strip().upper()
        
        # Common luminosity classes
        luminosity_classes = ['IA', 'IB', 'II', 'III', 'IV', 'V', 'VI', 'VII']
        
        for lum_class in luminosity_classes:
            if lum_class in spectral_class:
                return lum_class
                
        # Check for single Roman numerals
        if 'I' in spectral_class and 'V' not in spectral_class:
            return 'I'
        elif 'V' in spectral_class:
            return 'V'
            
        return 'Unknown'
        
    def _temperature_to_color_index(self, temperature: pd.Series) -> pd.Series:
        """Convert temperature to approximate B-V color index"""
        # Rough approximation based on main sequence stars
        # B-V = 0.92 * (5780/T - 1) for main sequence stars
        return 0.92 * (5780 / temperature - 1)
        
    def _estimate_stellar_mass(self, luminosity: pd.Series, temperature: pd.Series) -> pd.Series:
        """Estimate stellar mass using mass-luminosity relation"""
        # Very rough approximation: M/M_sun ≈ (L/L_sun)^0.25 for main sequence
        # This is a simplified relation and not accurate for all stellar types
        return np.power(luminosity, 0.25)
        
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics for the stellar data"""
        stats = {}
        
        numeric_columns = ['luminosity', 'temperature', 'radius', 'age', 'absolute_magnitude']
        
        for col in numeric_columns:
            if col in df.columns:
                stats[col] = {
                    'count': df[col].count(),
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'median': df[col].median()
                }
                
        # Spectral type distribution
        if 'spectral_type' in df.columns:
            stats['spectral_type_distribution'] = df['spectral_type'].value_counts().to_dict()
            
        # Luminosity class distribution
        if 'luminosity_class' in df.columns:
            stats['luminosity_class_distribution'] = df['luminosity_class'].value_counts().to_dict()
            
        return stats
        
    def filter_for_hr_diagram(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter data specifically for H-R diagram plotting"""
        # Ensure we have the required columns
        required_columns = ['luminosity', 'temperature']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in data")
                
        # Filter for reasonable H-R diagram ranges
        hr_df = df.copy()
        
        # Temperature range: roughly 2000K to 50000K (covers most stellar types)
        hr_df = hr_df[(hr_df['temperature'] >= 2000) & (hr_df['temperature'] <= 50000)]
        
        # Luminosity range: 10^-6 to 10^6 solar luminosities
        hr_df = hr_df[(hr_df['luminosity'] >= 1e-6) & (hr_df['luminosity'] <= 1e6)]
        
        logger.info(f"Filtered to {len(hr_df)} stars suitable for H-R diagram")
        
        return hr_df
