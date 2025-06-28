"""
Common Plotting Functions and Utilities

Centralized plotting utilities used across all AutoAnalytiX modules.
Provides consistent plot styling, saving, and verification functionality.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for file saving

import matplotlib.pyplot as plt
import seaborn as sns
import traceback
from pathlib import Path
from typing import Union, Optional, Tuple, Dict, Any
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore')


class PlotManager:
    """
    Centralized plot management utility for AutoAnalytiX.
    
    Handles plot styling, saving, verification, and error handling
    across all modules.
    """
    
    def __init__(self, logger=None):
        """
        Initialize PlotManager.
        
        Args:
            logger: Logger instance for tracking plot operations
        """
        self.logger = logger
        self.plots_created = []
        self._setup_plot_styling()
    
    def _setup_plot_styling(self):
        """Configure high-quality plotting defaults."""
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # High-quality plotting configuration
        plt.rcParams.update({
            'figure.figsize': (16, 12),
            'figure.dpi': 150,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'legend.fontsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10
        })
    
    def save_plot(
        self, 
        plot_path: Union[str, Path], 
        plot_name: str,
        dpi: int = 300,
        bbox_inches: str = 'tight'
    ) -> bool:
        """
        Save current plot with verification.
        
        Args:
            plot_path: Path where plot should be saved
            plot_name: Descriptive name for logging
            dpi: Resolution for saved plot
            bbox_inches: Bounding box setting
            
        Returns:
            bool: True if plot saved successfully
        """
        try:
            plot_path = Path(plot_path)
            
            # Ensure directory exists
            plot_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save plot
            plt.savefig(plot_path, dpi=dpi, bbox_inches=bbox_inches)
            plt.close()
            
            # Verify plot creation
            success = self._verify_plot_creation(plot_path, plot_name)
            
            if success:
                self._track_plot_created(plot_path, plot_name)
            
            return success
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Failed to save plot {plot_name}: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            plt.close('all')  # Ensure cleanup
            return False
    
    def _verify_plot_creation(self, plot_path: Path, plot_name: str) -> bool:
        """
        Verify plot was actually created and has content.
        
        Args:
            plot_path: Path to the plot file
            plot_name: Name of the plot for logging
            
        Returns:
            bool: True if plot exists and has reasonable size
        """
        try:
            if plot_path.exists():
                size = plot_path.stat().st_size
                if size > 1000:  # Reasonable minimum size for a plot
                    if self.logger:
                        self.logger.info(f"[OK] Plot saved: {plot_name} ({size} bytes)")
                    return True
                else:
                    if self.logger:
                        self.logger.error(f"[ERROR] Plot file too small: {plot_name} ({size} bytes)")
            else:
                if self.logger:
                    self.logger.error(f"[ERROR] Plot NOT created: {plot_name}")
            return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Error verifying plot {plot_name}: {e}")
            return False
    
    def _track_plot_created(self, plot_path: Path, plot_name: str):
        """Track plots created for summary reporting."""
        self.plots_created.append({
            'file_path': str(plot_path),
            'plot_name': plot_name,
            'size_bytes': plot_path.stat().st_size if plot_path.exists() else 0
        })
    
    def create_figure(
        self, 
        figsize: Tuple[int, int] = (16, 12), 
        nrows: int = 1, 
        ncols: int = 1
    ) -> Tuple:
        """
        Create figure with standard styling.
        
        Args:
            figsize: Figure size as (width, height)
            nrows: Number of subplot rows
            ncols: Number of subplot columns
            
        Returns:
            Tuple: (figure, axes) from plt.subplots()
        """
        try:
            fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
            return fig, axes
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Failed to create figure: {e}")
            return None, None
    
    def setup_axis(
        self, 
        ax, 
        title: str = None, 
        xlabel: str = None, 
        ylabel: str = None,
        grid: bool = True,
        grid_alpha: float = 0.3
    ):
        """
        Apply standard axis formatting.
        
        Args:
            ax: Matplotlib axis object
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            grid: Whether to show grid
            grid_alpha: Grid transparency
        """
        try:
            if title:
                ax.set_title(title, fontweight='bold')
            if xlabel:
                ax.set_xlabel(xlabel, fontweight='bold')
            if ylabel:
                ax.set_ylabel(ylabel, fontweight='bold')
            if grid:
                ax.grid(True, alpha=grid_alpha)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Failed to setup axis: {e}")
    
    def add_value_labels_to_bars(self, ax, bars, values, format_string: str = "{:.0f}"):
        """
        Add value labels on top of bars.
        
        Args:
            ax: Matplotlib axis object
            bars: Bar container from ax.bar()
            values: Values to display
            format_string: Format string for values
        """
        try:
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2., 
                    height + max(values)*0.01,
                    format_string.format(value), 
                    ha='center', 
                    va='bottom', 
                    fontweight='bold'
                )
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Failed to add value labels: {e}")
    
    def create_color_map(self, categories: list, palette: str = "husl") -> Dict[str, str]:
        """
        Create consistent color mapping for categories.
        
        Args:
            categories: List of category names
            palette: Seaborn palette name
            
        Returns:
            Dict: Mapping of category -> color
        """
        try:
            colors = sns.color_palette(palette, len(categories))
            return dict(zip(categories, colors))
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Failed to create color map: {e}")
            return {}
    
    def cleanup_plots(self):
        """Close all open plots to free memory."""
        try:
            plt.close('all')
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Failed to cleanup plots: {e}")
    
    def create_standard_threat_colors(self) -> Dict[str, str]:
        """Create standard color mapping for threat levels."""
        return {
            'CRITICAL': 'darkred',
            'HIGH': 'red', 
            'MEDIUM': 'orange',
            'LOW': 'yellow',
            'NORMAL': 'green'
        }
    
    def create_utilization_colors(self) -> Dict[str, str]:
        """Create standard color mapping for utilization analysis."""
        return {
            'EXCELLENT': 'darkgreen',
            'GOOD': 'green',
            'FAIR': 'orange', 
            'POOR': 'red',
            'ACTIVE': 'green',
            'IDLE': 'red'
        }
    
    def apply_tight_layout(self):
        """Apply tight layout with error handling."""
        try:
            plt.tight_layout()
        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️  Tight layout failed: {e}")
    
    def get_plots_summary(self) -> Dict[str, Any]:
        """
        Get summary of all plots created.
        
        Returns:
            Dict: Summary statistics of plots created
        """
        return {
            'total_plots': len(self.plots_created),
            'plots': self.plots_created,
            'total_size_bytes': sum(plot.get('size_bytes', 0) for plot in self.plots_created)
        }
    
    def safe_plot_execution(self, plot_function, *args, **kwargs):
        """
        Execute plotting function with comprehensive error handling.
        
        Args:
            plot_function: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            bool: True if execution successful
        """
        try:
            plot_function(*args, **kwargs)
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Plot execution failed: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.cleanup_plots()
            return False