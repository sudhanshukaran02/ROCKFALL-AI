"""
Spatial Terrain Intelligence Module for Rockfall AI.

Derives terrain morphological features from a Digital Elevation Model (DEM) raster file:
- Elevation
- Slope (degrees)
- Aspect (degrees 0-360)
- Terrain Curvature (Laplacian second derivative)
- Terrain Roughness Index (TRI - local 3x3 std dev)
- Topographic Wetness Index (TWI - ln(a / tan(beta)))

Preserves CRS, resolution, affine spatial transform, and NoData masks.
Saves derived GeoTIFF layers and PNG visualizations to results/terrain/
"""

import os
import numpy as np
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt

try:
    import rasterio
    from rasterio.transform import Affine
except ImportError:
    rasterio = None

class TerrainFeatureExtractor:
    def __init__(self, dem_path, output_dir=os.path.join('results', 'terrain')):
        """
        Initializes the feature extractor with a input DEM GeoTIFF.
        
        Parameters:
            dem_path (str): File path to input DEM raster file (.tif)
            output_dir (str): Destination directory for derived layers
        """
        if rasterio is None:
            raise ImportError("rasterio is required for DEM processing. Install via 'pip install rasterio'")
            
        if not os.path.exists(dem_path):
            raise FileNotFoundError(f"Input DEM raster file not found at '{dem_path}'.")
            
        self.dem_path = dem_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Open DEM and read metadata
        with rasterio.open(dem_path) as src:
            self.crs = src.crs
            self.transform = src.transform
            self.nodata = src.nodata
            self.profile = src.profile.copy()
            self.bounds = src.bounds
            self.res = src.res  # (pixel_width, pixel_height)
            self.elevation_data = src.read(1).astype(np.float64)
            
        # Handle NoData Masking
        self.mask = np.ones_like(self.elevation_data, dtype=bool)
        if self.nodata is not None:
            if np.isnan(self.nodata):
                self.mask = ~np.isnan(self.elevation_data)
            else:
                self.mask = (self.elevation_data != self.nodata)
                
        # Fill NoData temporarily with nearest neighbor or nan for calculations
        self.clean_elevation = self.elevation_data.copy()
        if not np.all(self.mask):
            self.clean_elevation[~self.mask] = np.nan

        # Determine cell ground size in meters (for geographic CRS like EPSG:4326)
        if self.crs is not None and getattr(self.crs, 'is_geographic', False):
            lat_center = (self.bounds.bottom + self.bounds.top) / 2.0
            lat_rad = np.radians(lat_center)
            self.dy_m = abs(self.res[1]) * 111320.0
            self.dx_m = abs(self.res[0]) * 111320.0 * np.cos(lat_rad)
        else:
            self.dx_m = abs(self.res[0])
            self.dy_m = abs(self.res[1])

    def compute_slope_and_aspect(self):
        """Calculates slope angle (degrees) and aspect (degrees 0-360)."""
        dx, dy = self.dx_m, self.dy_m
        
        # Calculate gradients using Sobel operators
        dz_dx = ndimage.sobel(self.clean_elevation, axis=1) / (8.0 * dx)
        dz_dy = ndimage.sobel(self.clean_elevation, axis=0) / (8.0 * dy)
        
        # Slope magnitude
        slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
        slope_deg = np.degrees(slope_rad)
        
        # Aspect (0 degrees = North, 90 = East, 180 = South, 270 = West)
        aspect_rad = np.arctan2(-dz_dy, dz_dx)
        aspect_deg = np.degrees(aspect_rad)
        aspect_deg = (90.0 - aspect_deg) % 360.0
        
        # Mask NoData areas
        slope_deg[~self.mask] = np.nan
        aspect_deg[~self.mask] = np.nan
        
        return slope_deg, aspect_deg

    def compute_curvature(self):
        """Calculates terrain curvature (Laplacian second derivative)."""
        dx, dy = self.dx_m, self.dy_m
        
        kernel = np.array([[0, 1, 0],
                           [1, -4, 1],
                           [0, 1, 0]], dtype=float) / ((dx + dy) / 2.0)**2
                           
        curvature = ndimage.convolve(self.clean_elevation, kernel, mode='nearest')
        curvature[~self.mask] = np.nan
        return curvature

    def compute_roughness(self):
        """Calculates Terrain Roughness Index (TRI - local 3x3 standard deviation)."""
        def local_std(arr):
            mean = ndimage.uniform_filter(arr, size=3, mode='nearest')
            sqr_mean = ndimage.uniform_filter(arr**2, size=3, mode='nearest')
            var = np.maximum(0.0, sqr_mean - mean**2)
            return np.sqrt(var)
            
        roughness = local_std(self.clean_elevation)
        roughness[~self.mask] = np.nan
        return roughness

    def compute_twi(self, slope_deg):
        """
        Calculates Topographic Wetness Index (TWI = ln(a / tan(beta))).
        Approximates specific catchment area 'a' using flow accumulation.
        """
        dx, dy = self.dx_m, self.dy_m
        cell_area = dx * dy
        
        # Convert slope to radians, avoiding 0 slope DivisionByZero
        slope_rad = np.radians(np.maximum(slope_deg, 0.1))
        tan_slope = np.tan(slope_rad)
        
        # Approximate cumulative upslope area using distance gradient proxy
        dz_dx = np.abs(ndimage.sobel(self.clean_elevation, axis=1) / (8.0 * dx))
        dz_dy = np.abs(ndimage.sobel(self.clean_elevation, axis=0) / (8.0 * dy))
        grad_mag = np.sqrt(dz_dx**2 + dz_dy**2) + 1e-4
        
        # Upslope area proxy
        catchment_area = cell_area * (1.0 + ndimage.gaussian_filter(grad_mag, sigma=2.0) * 10.0)
        
        twi = np.log(catchment_area / tan_slope)
        twi[~self.mask] = np.nan
        return twi

    def process_all_layers(self):
        """Derives all terrain features and saves GeoTIFF rasters + PNG plots."""
        print(f"\nProcessing DEM: '{self.dem_path}'")
        print(f"  Raster Size: {self.elevation_data.shape[1]}x{self.elevation_data.shape[0]} | Resolution: {self.res} | CRS: {self.crs}")
        
        slope_deg, aspect_deg = self.compute_slope_and_aspect()
        curvature = self.compute_curvature()
        roughness = self.compute_roughness()
        twi = self.compute_twi(slope_deg)
        
        layers = {
            'elevation': (self.clean_elevation, 'terrain', 'Elevation (m)'),
            'slope': (slope_deg, 'magma', 'Slope (degrees)'),
            'aspect': (aspect_deg, 'twilight', 'Aspect (degrees)'),
            'curvature': (curvature, 'coolwarm', 'Curvature (Laplacian)'),
            'roughness': (roughness, 'viridis', 'Terrain Roughness Index'),
            'twi': (twi, 'YlGnBu', 'Topographic Wetness Index (TWI)')
        }
        
        saved_files = []
        
        # Save GeoTIFFs & PNG Visualizations
        for name, (arr, cmap, title) in layers.items():
            tif_path = os.path.join(self.output_dir, f"{name}.tif")
            png_path = os.path.join(self.output_dir, f"{name}.png")
            
            # Save GeoTIFF preserving CRS and Transform
            profile = self.profile.copy()
            profile.update(dtype=rasterio.float32, count=1, nodata=-9999.0)
            
            out_arr = np.where(np.isnan(arr), -9999.0, arr).astype(np.float32)
            
            with rasterio.open(tif_path, 'w', **profile) as dst:
                dst.write(out_arr, 1)
            saved_files.append(tif_path)
            
            # Save PNG Plot
            plt.figure(figsize=(8, 6))
            im_arr = np.where(np.isnan(arr), np.nan, arr)
            plt.imshow(im_arr, cmap=cmap, extent=[self.bounds.left, self.bounds.right, self.bounds.bottom, self.bounds.top])
            plt.colorbar(label=title)
            plt.title(f"{title}\nDhanbad SRTM Terrain Analysis — Prototype")
            plt.xlabel("Longitude (°E)")
            plt.ylabel("Latitude (°N)")
            plt.tight_layout()
            plt.savefig(png_path, dpi=300)
            plt.close()
            saved_files.append(png_path)
            
            print(f"  [Saved] {tif_path} & {png_path}")
            
        return saved_files
