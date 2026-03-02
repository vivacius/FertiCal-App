import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box
from scipy.spatial import cKDTree
from pykrige.ok import OrdinaryKriging
import logging
import config

logger = logging.getLogger(__name__)

def create_grid(geometry, cell_size=20):
    """
    Creates a regular grid of points within the bounding box of the geometry.
    Equivalent to R's expand.grid over bbox with buffering.
    """
    bounds = geometry.total_bounds
    # R uses a buffer of 50m for the extent, we mimic that
    minx, miny, maxx, maxy = bounds
    # R: ext = gBuffer(poli, width = 50, quadsegs = 1)@bbox
    # We add 50m buffer conceptually to the grid extent
    minx -= 50; miny -= 50; maxx += 50; maxy += 50
    
    x_coords = np.arange(minx, maxx + cell_size, cell_size)
    y_coords = np.arange(miny, maxy + cell_size, cell_size)
    
    xx, yy = np.meshgrid(x_coords, y_coords)
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    
    return pd.DataFrame(grid_points, columns=['x', 'y'])

def idw_interpolation(known_points, known_values, target_points, power=0.5, k=20):
    """
    Inverse Distance Weighting Interpolation matching R's gstat.
    
    Args:
        known_points (np.array): (N, 2) array of x, y coordinates
        known_values (np.array): (N,) array of values
        target_points (np.array): (M, 2) array of target x, y
        power (float): IDW power (idp in R)
        k (int): Number of neighbors (nmax in R)
        
    Returns:
        np.array: Interpolated values
    """
    tree = cKDTree(known_points)
    dist, idx = tree.query(target_points, k=k)
    
    # Avoid division by zero
    dist = np.maximum(dist, 1e-10)
    
    weights = 1.0 / (dist ** power)
    # Sum weights per row
    weights_sum = np.sum(weights, axis=1)
    
    # Calculate weighted average
    # known_values[idx] gets the values of neighbors
    # sum(weights * values) / sum(weights)
    neighbor_values = known_values[idx]
    numerator = np.sum(weights * neighbor_values, axis=1)
    
    interpolated = numerator / weights_sum
    return interpolated

def kriging_interpolation(known_points, known_values, target_points, nugget, sill, range_val, model='spherical'):
    """
    Ordinary Kriging interpolation using PyKrige.
    Maps R geoR parameters:
    - sigmasq (partial sill) -> sill (in pykrige sill usually means partial sill + nugget, but we check variogram_model_parameters)
    - phi (range parameter) -> range
    - nugget -> nugget
    
    Warning: R's krige.conv uses covariance parameters directly.
    PyKrige's OrdinaryKriging takes a VariogramModel.
    We pass 'custom' or standard models with specified parameters.
    """
    try:
        # PyKrige parameters for variogram_model_parameters are usually [sill, range, nugget]
        # depending on the function.
        # For spherical: gamma(h) = c0 + c * (1.5*h/a - 0.5*(h/a)^3)
        # R cov.pars = c(sigmasq, phi) -> sigmasq is partial sill (c), phi is range param
        
        ok = OrdinaryKriging(
            known_points[:, 0], 
            known_points[:, 1], 
            known_values, 
            variogram_model=model,
            variogram_parameters=[sill, range_val, nugget], # [partial_sill, range, nugget] for spherical
            verbose=False
        )
        
        z, ss = ok.execute('points', target_points[:, 0], target_points[:, 1])
        return z
        
    except Exception as e:
        logger.error(f"Kriging failed: {e}")
        # Fallback to IDW if Kriging fails (robustness)
        logger.warning("Falling back to IDW due to Kriging failure")
        return idw_interpolation(known_points, known_values, target_points)

def mask_grid_to_polygon(grid_df, polygon_gdf):
    """
    Clips the grid points to those contained within the polygon.
    Equivalent to R's mask or intersect.
    """
    points_gdf = gpd.GeoDataFrame(
        grid_df, 
        geometry=gpd.points_from_xy(grid_df.x, grid_df.y)
    )
    # Ensure CRS match (assuming projected system like EPSG:32618 / 21896 for Colombia)
    # For now we assume they are already in the same projected CRS from the input files
    
    # Spatial join or within check
    # Using intersect which is safer for points on boundary
    masked = gpd.tools.sjoin(points_gdf, polygon_gdf, predicate='within', how='inner')
    
    return masked[['x', 'y', 'geometry']].reset_index(drop=True)

def extract_zonal_stats(gdf, raster_col_name):
    """
    Calculates statistics (mean) for the polygon.
    Since we are working with points inside the polygon (vectorized raster),
    we can just take the mean of the points column.
    """
    return gdf[raster_col_name].mean()
