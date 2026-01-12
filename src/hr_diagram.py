"""
Hertzsprung-Russell diagram generation
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

from .config import HR_DIAGRAM_CONFIG

logger = logging.getLogger(__name__)


class HRDiagramGenerator:
    """Generate Hertzsprung-Russell diagrams from stellar data"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or HR_DIAGRAM_CONFIG
        
        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Spectral type colors (approximate)
        self.spectral_colors = {
            'O': '#9bb0ff',  # Blue
            'B': '#aabfff',  # Blue-white
            'A': '#cad7ff',  # White
            'F': '#f8f7ff',  # Yellow-white
            'G': '#fff4ea',  # Yellow (like our Sun)
            'K': '#ffd2a1',  # Orange
            'M': '#ffad51',  # Red
            'L': '#ff6b6b',  # Brown dwarf
            'T': '#ff4757',  # Brown dwarf
            'Y': '#ff3838',  # Brown dwarf
            'Unknown': '#95a5a6'  # Gray
        }
        
    def create_hr_diagram(self, df: pd.DataFrame, output_path: str = None, famous_systems: Dict = None) -> str:
        """Create a Hertzsprung-Russell diagram"""
        logger.info(f"Creating H-R diagram with {len(df)} stars...")
        
        # Set up the figure
        fig, ax = plt.subplots(figsize=self.config['figsize'], dpi=self.config['dpi'])
        
        # Create the main scatter plot
        self._plot_main_sequence(ax, df)
        
        # Add famous systems if provided
        if famous_systems:
            self._add_famous_systems(ax, famous_systems)
        
        # Add stellar evolution tracks if we have enough data
        self._add_evolution_tracks(ax, df)
        
        # Customize the plot
        self._customize_plot(ax, df)
        
        # Add annotations and legends
        self._add_annotations(ax, df, famous_systems)
        
        # Save the plot
        if output_path is None:
            output_path = "output/hr_diagram_new_eden.png"
            
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()
        
        logger.info(f"H-R diagram saved to: {output_path}")
        return output_path
        
    def _plot_main_sequence(self, ax, df: pd.DataFrame):
        """Plot the main stellar data points"""
        
        # Color by spectral type if available
        if 'spectral_type' in df.columns:
            for spec_type in df['spectral_type'].unique():
                if pd.isna(spec_type):
                    continue
                    
                mask = df['spectral_type'] == spec_type
                subset = df[mask]
                
                color = self.spectral_colors.get(spec_type, '#95a5a6')
                
                ax.scatter(
                    subset['temperature'], 
                    subset['luminosity'],
                    c=color,
                    alpha=self.config['alpha'],
                    s=self.config['marker_size'],
                    label=f'{spec_type} ({len(subset)})',
                    edgecolors='black',
                    linewidth=0.5
                )
        else:
            # Fallback: color by temperature
            scatter = ax.scatter(
                df['temperature'], 
                df['luminosity'],
                c=df['temperature'],
                cmap='coolwarm_r',  # Reverse so hot stars are blue
                alpha=self.config['alpha'],
                s=self.config['marker_size'],
                edgecolors='black',
                linewidth=0.5
            )
            plt.colorbar(scatter, ax=ax, label='Temperature (K)')
            
    def _add_famous_systems(self, ax, famous_systems: Dict):
        """Add famous EVE Online systems to the H-R diagram"""
        
        # Define system categories and their styling
        system_categories = {
            'Trade Hubs': {
                'systems': ['Jita', 'Amarr', 'Rens', 'Hek', 'Dodixie'],
                'color': '#FFD700',  # Gold
                'marker': 's',       # Square
                'size': 150,
                'edge_color': '#B8860B'
            },
            'PvP Hotspots': {
                'systems': ['Amamake', 'Auga', 'Tama'],
                'color': '#FF4500',  # Red-Orange
                'marker': '^',       # Triangle
                'size': 120,
                'edge_color': '#8B0000'
            },
            'Null-Sec Systems': {
                'systems': ['R-6KYM', '1DQ1-A'],
                'color': '#8A2BE2',  # Blue-Violet
                'marker': 'D',       # Diamond
                'size': 120,
                'edge_color': '#4B0082'
            },
            'Other Notable': {
                'systems': ['Vard', 'Ahbazon', 'Sosala'],
                'color': '#00CED1',  # Dark Turquoise
                'marker': 'o',       # Circle
                'size': 100,
                'edge_color': '#008B8B'
            }
        }
        
        plotted_systems = []
        
        for category, style in system_categories.items():
            category_systems = []
            
            for system_name in style['systems']:
                if system_name in famous_systems and famous_systems[system_name] is not None:
                    system_data = famous_systems[system_name]
                    stellar_data = system_data['stellar_data']
                    
                    if 'temperature' in stellar_data and 'luminosity' in stellar_data:
                        temp = stellar_data['temperature']
                        lum = stellar_data['luminosity']
                        
                        # Plot the system
                        ax.scatter(temp, lum, 
                                 c=style['color'], 
                                 marker=style['marker'],
                                 s=style['size'],
                                 edgecolors=style['edge_color'],
                                 linewidth=2,
                                 alpha=0.9,
                                 zorder=10)  # Ensure famous systems are on top
                        
                        # Add system name annotation
                        ax.annotate(system_name, 
                                   xy=(temp, lum),
                                   xytext=(8, 8), 
                                   textcoords='offset points',
                                   fontsize=9,
                                   fontweight='bold',
                                   bbox=dict(boxstyle='round,pad=0.3', 
                                           facecolor=style['color'], 
                                           alpha=0.8,
                                           edgecolor=style['edge_color']),
                                   arrowprops=dict(arrowstyle='->', 
                                                 connectionstyle='arc3,rad=0.1',
                                                 color=style['edge_color']))
                        
                        category_systems.append(system_name)
                        plotted_systems.append(system_name)
            
            # Add category to legend if we have systems in this category
            if category_systems:
                ax.scatter([], [], c=style['color'], marker=style['marker'], 
                          s=style['size'], edgecolors=style['edge_color'], 
                          linewidth=2, alpha=0.9, label=f"{category} ({len(category_systems)})")
        
        if plotted_systems:
            logger.info(f"Added {len(plotted_systems)} famous systems to H-R diagram: {', '.join(plotted_systems)}")
        else:
            logger.warning("No famous systems could be plotted on the H-R diagram")
            
    def _add_evolution_tracks(self, ax, df: pd.DataFrame):
        """Add theoretical stellar evolution tracks"""
        # This is a simplified representation
        # In reality, you'd need stellar evolution models
        
        # Main sequence approximation (very rough)
        temp_range = np.logspace(3.3, 4.7, 100)  # 2000K to 50000K
        
        # Rough main sequence relation: L ∝ T^4 (Stefan-Boltzmann) modified
        # This is highly simplified and not accurate for real stellar physics
        main_sequence_lum = np.power(temp_range / 5780, 3.5)  # Normalized to Sun
        
        ax.plot(temp_range, main_sequence_lum, 'k--', alpha=0.7, linewidth=2, 
                label='Approximate Main Sequence')
                
        # Giant branch (very rough approximation)
        giant_temps = np.linspace(3000, 5000, 50)
        giant_lums = np.power(10, np.linspace(1, 3, 50))  # 10 to 1000 L_sun
        ax.plot(giant_temps, giant_lums, 'r:', alpha=0.7, linewidth=2,
                label='Approximate Giant Branch')
                
    def _customize_plot(self, ax, df: pd.DataFrame):
        """Customize the plot appearance"""
        
        # Set labels
        ax.set_xlabel(self.config['xlabel'], fontsize=14)
        ax.set_ylabel(self.config['ylabel'], fontsize=14)
        ax.set_title(self.config['title'], fontsize=16, fontweight='bold')
        
        # Set scales
        if self.config['log_scale_y']:
            ax.set_yscale('log')
            
        # Invert x-axis (hot stars on the left, cool on the right)
        if self.config['invert_x']:
            ax.invert_xaxis()
            
        # Set reasonable limits
        temp_min, temp_max = df['temperature'].min(), df['temperature'].max()
        lum_min, lum_max = df['luminosity'].min(), df['luminosity'].max()
        
        # Add some padding
        temp_padding = (temp_max - temp_min) * 0.1
        ax.set_xlim(temp_max + temp_padding, temp_min - temp_padding)
        
        if self.config['log_scale_y']:
            ax.set_ylim(lum_min * 0.5, lum_max * 2)
        else:
            lum_padding = (lum_max - lum_min) * 0.1
            ax.set_ylim(lum_min - lum_padding, lum_max + lum_padding)
            
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Tick formatting
        ax.tick_params(labelsize=12)
        
    def _add_annotations(self, ax, df: pd.DataFrame, famous_systems: Dict = None):
        """Add annotations and legends to the plot"""
        
        # Legend - combine spectral types and famous systems
        legend_elements = []
        
        # Add spectral type legend elements
        if 'spectral_type' in df.columns:
            for spec_type in df['spectral_type'].unique():
                if pd.isna(spec_type):
                    continue
                count = len(df[df['spectral_type'] == spec_type])
                color = self.spectral_colors.get(spec_type, '#95a5a6')
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                markerfacecolor=color, markersize=8,
                                                label=f'{spec_type} ({count})', 
                                                markeredgecolor='black', markeredgewidth=0.5))
        
        # Get existing legend elements from famous systems (if any)
        existing_legend = ax.get_legend()
        if existing_legend:
            for handle in existing_legend.legendHandles:
                if hasattr(handle, '_label') and any(cat in handle._label for cat in ['Trade Hubs', 'PvP Hotspots', 'Null-Sec', 'Other Notable']):
                    legend_elements.append(handle)
        
        # Create combined legend
        if legend_elements:
            # Split into two columns if we have many elements
            ncol = 2 if len(legend_elements) > 8 else 1
            legend = ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), 
                             loc='upper left', fontsize=9, ncol=ncol,
                             title='Spectral Types & Famous Systems')
            legend.get_title().set_fontsize(11)
        else:
            ax.legend(fontsize=10)
            
        # Add strategic systems if available
        self._add_strategic_systems(ax, df)
        
        # Add some reference points if we can identify them
        self._add_reference_stars(ax, df)
        
        # Add statistics text box (updated to include famous systems info)
        self._add_statistics_box(ax, df, famous_systems)
        
    def _add_strategic_systems(self, ax, df: pd.DataFrame):
        """Add highlighting for strategic EVE Online systems"""
        
        # Check if we have strategic systems data
        strategic_stars = df[df['is_strategic'] == True] if 'is_strategic' in df.columns else pd.DataFrame()
        
        if strategic_stars.empty:
            logger.info("No strategic systems data found for highlighting")
            return
            
        logger.info(f"Highlighting {len(strategic_stars)} strategic systems on HR diagram")
        
        # Plot strategic systems with distinctive markers
        ax.scatter(
            strategic_stars['temperature'], 
            strategic_stars['luminosity'],
            c=self.config['strategic_color'],
            alpha=self.config['strategic_alpha'],
            s=self.config['strategic_marker_size'],
            edgecolors=self.config['strategic_edge_color'],
            linewidth=self.config['strategic_edge_width'],
            marker='x',  # X shape for strategic systems as requested
            label=f'Strategic Systems ({len(strategic_stars)})',
            zorder=10  # Ensure they appear on top
        )
        
        # Add labels for each strategic system
        for _, star in strategic_stars.iterrows():
            if 'strategic_system_name' in star and pd.notna(star['strategic_system_name']):
                # Position label slightly offset from the star
                ax.annotate(
                    star['strategic_system_name'], 
                    xy=(star['temperature'], star['luminosity']),
                    xytext=(12, 12), 
                    textcoords='offset points',
                    fontsize=9,
                    fontweight='bold',
                    color='black',
                    bbox=dict(
                        boxstyle='round,pad=0.3', 
                        facecolor='yellow', 
                        alpha=0.9,
                        edgecolor='black',
                        linewidth=1.5
                    ),
                    arrowprops=dict(
                        arrowstyle='->', 
                        connectionstyle='arc3,rad=0.2',
                        color='black',
                        lw=1.5
                    ),
                    zorder=11
                )
                
        # Update legend to include strategic systems
        handles, labels = ax.get_legend_handles_labels()
        if handles:  # Only update if there are existing legend items
            ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left', 
                     fontsize=10, title='Spectral Type & Strategic Systems')

    def _add_reference_stars(self, ax, df: pd.DataFrame):
        """Add annotations for notable stars if identifiable"""
        
        # Try to identify Sun-like stars (G-type, ~5780K, ~1 L_sun)
        if 'spectral_type' in df.columns:
            sun_like = df[
                (df['spectral_type'] == 'G') & 
                (df['temperature'].between(5500, 6000)) &
                (df['luminosity'].between(0.8, 1.2))
            ]
            
            if len(sun_like) > 0:
                # Annotate one representative Sun-like star
                star = sun_like.iloc[0]
                ax.annotate('Sun-like star', 
                           xy=(star['temperature'], star['luminosity']),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
                           
    def _add_statistics_box(self, ax, df: pd.DataFrame, famous_systems: Dict = None):
        """Add a statistics box to the plot"""
        
        stats_text = f"Total Stars: {len(df):,}\n"
        
        if 'spectral_type' in df.columns:
            most_common = df['spectral_type'].value_counts().head(3)
            stats_text += "Most Common Types:\n"
            for spec_type, count in most_common.items():
                percentage = count / len(df) * 100
                stats_text += f"  {spec_type}: {count} ({percentage:.1f}%)\n"
                
        # Temperature range
        temp_range = df['temperature'].max() - df['temperature'].min()
        stats_text += f"\nTemp Range: {temp_range:,.0f} K"
        
        # Luminosity range
        lum_range = df['luminosity'].max() / df['luminosity'].min()
        stats_text += f"\nLum Range: {lum_range:.1e}×"
        
        # Add famous systems info if available
        if famous_systems:
            successful_systems = sum(1 for v in famous_systems.values() if v is not None)
            total_systems = len(famous_systems)
            stats_text += f"\n\nFamous Systems: {successful_systems}/{total_systems}"
        
        # Add the text box
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', horizontalalignment='left',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
                fontsize=9, family='monospace')
                
    def create_detailed_analysis(self, df: pd.DataFrame, output_dir: str = "output") -> Dict[str, str]:
        """Create additional analysis plots"""
        
        output_files = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. Spectral type distribution
        if 'spectral_type' in df.columns:
            plt.figure(figsize=(10, 6))
            spec_counts = df['spectral_type'].value_counts()
            spec_counts.plot(kind='bar', color=[self.spectral_colors.get(x, '#95a5a6') for x in spec_counts.index])
            plt.title('Spectral Type Distribution in New Eden')
            plt.xlabel('Spectral Type')
            plt.ylabel('Number of Stars')
            plt.xticks(rotation=0)
            plt.tight_layout()
            
            spec_dist_path = output_path / "spectral_distribution.png"
            plt.savefig(spec_dist_path, dpi=300, bbox_inches='tight')
            plt.close()
            output_files['spectral_distribution'] = str(spec_dist_path)
            
        # 2. Temperature vs Luminosity correlation
        plt.figure(figsize=(10, 6))
        plt.scatter(df['temperature'], df['luminosity'], alpha=0.6)
        plt.xlabel('Temperature (K)')
        plt.ylabel('Luminosity (Solar Luminosities)')
        plt.title('Temperature vs Luminosity Correlation')
        plt.yscale('log')
        
        # Add correlation coefficient
        corr = df['temperature'].corr(np.log10(df['luminosity']))
        plt.text(0.05, 0.95, f'Correlation: {corr:.3f}', transform=plt.gca().transAxes,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        temp_lum_path = output_path / "temperature_luminosity_correlation.png"
        plt.savefig(temp_lum_path, dpi=300, bbox_inches='tight')
        plt.close()
        output_files['temp_lum_correlation'] = str(temp_lum_path)
        
        # 3. Stellar parameter histograms
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Temperature histogram
        axes[0, 0].hist(df['temperature'], bins=50, alpha=0.7, color='orange')
        axes[0, 0].set_xlabel('Temperature (K)')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].set_title('Temperature Distribution')
        
        # Luminosity histogram (log scale)
        axes[0, 1].hist(np.log10(df['luminosity']), bins=50, alpha=0.7, color='red')
        axes[0, 1].set_xlabel('Log₁₀(Luminosity)')
        axes[0, 1].set_ylabel('Count')
        axes[0, 1].set_title('Luminosity Distribution')
        
        # Radius histogram (if available)
        if 'radius' in df.columns:
            axes[1, 0].hist(df['radius'], bins=50, alpha=0.7, color='blue')
            axes[1, 0].set_xlabel('Radius (Solar Radii)')
            axes[1, 0].set_ylabel('Count')
            axes[1, 0].set_title('Radius Distribution')
        else:
            axes[1, 0].text(0.5, 0.5, 'Radius data\nnot available', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            
        # Age histogram (if available)
        if 'age' in df.columns:
            axes[1, 1].hist(df['age'], bins=50, alpha=0.7, color='green')
            axes[1, 1].set_xlabel('Age (years)')
            axes[1, 1].set_ylabel('Count')
            axes[1, 1].set_title('Age Distribution')
        else:
            axes[1, 1].text(0.5, 0.5, 'Age data\nnot available', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
        
        plt.tight_layout()
        histograms_path = output_path / "stellar_parameter_histograms.png"
        plt.savefig(histograms_path, dpi=300, bbox_inches='tight')
        plt.close()
        output_files['parameter_histograms'] = str(histograms_path)
        
        logger.info(f"Created {len(output_files)} additional analysis plots")
        return output_files
