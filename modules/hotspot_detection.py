import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

@st.cache_data(show_spinner="Computing DBSCAN hotspots...")
def _run_dbscan_cached(coords_array: np.ndarray, eps_rad: float, min_samples: int) -> np.ndarray:
    """Cached DBSCAN execution."""
    dbscan = DBSCAN(metric='haversine', eps=eps_rad, min_samples=min_samples, algorithm='ball_tree')
    return dbscan.fit_predict(coords_array)

class HotspotDetector:
    """
    Detects and analyzes geographic hotspots of civic complaints using DBSCAN clustering.
    """

    def __init__(self, eps_km: float = 0.5, min_samples: int = 5):
        """
        Initialize the HotspotDetector.

        Args:
            eps_km (float): Radius in kilometers.
            min_samples (int): Core sample minimum count.
        """
        self.eps_km = eps_km
        self.eps_rad = eps_km / 6371.0
        self.min_samples = min_samples

    def detect_hotspots(self, df: pd.DataFrame, lat_col: str = 'latitude', lon_col: str = 'longitude') -> pd.DataFrame:
        """
        Detect hotspots in the given dataframe based on latitude and longitude.

        Args:
            df (pd.DataFrame): DataFrame containing complaint data.
            lat_col (str): Name of the latitude column.
            lon_col (str): Name of the longitude column.

        Returns:
            pd.DataFrame: A copy of the input DataFrame with an added 'cluster_id' column.
        """
        df_copy = df.copy()
        
        if df_copy.empty or lat_col not in df_copy.columns or lon_col not in df_copy.columns:
            df_copy['cluster_id'] = -1
            return df_copy
            
        coords = np.radians(df_copy[[lat_col, lon_col]].values)
        df_copy['cluster_id'] = _run_dbscan_cached(coords, self.eps_rad, self.min_samples)
        
        return df_copy

    def summarize_hotspots(self, df_with_clusters: pd.DataFrame, cluster_col: str = 'cluster_id') -> pd.DataFrame:
        """
        Summarize the detected hotspots.

        Args:
            df_with_clusters (pd.DataFrame): DataFrame with cluster IDs.
            cluster_col (str): Name of the cluster ID column.

        Returns:
            pd.DataFrame: Summary of hotspots sorted by complaint count descending.
        """
        valid_clusters = df_with_clusters[df_with_clusters[cluster_col] != -1]
        
        if valid_clusters.empty:
            return pd.DataFrame()
            
        summary_records = []
        grouped = valid_clusters.groupby(cluster_col)
        
        for cluster_id, group in grouped:
            record = {
                'cluster_id': cluster_id,
                'complaint_count': len(group),
                'centroid_lat': group['latitude'].mean() if 'latitude' in group.columns else np.nan,
                'centroid_lon': group['longitude'].mean() if 'longitude' in group.columns else np.nan,
            }
            
            if 'category' in group.columns:
                record['dominant_category'] = group['category'].mode().iloc[0] if not group['category'].mode().empty else np.nan
                
            if 'resolution_time_hours' in group.columns:
                record['avg_resolution_time'] = group['resolution_time_hours'].mean()
            else:
                record['avg_resolution_time'] = np.nan
                
            summary_records.append(record)
            
        summary_df = pd.DataFrame(summary_records)
        summary_df = summary_df.sort_values(by='complaint_count', ascending=False).reset_index(drop=True)
        return summary_df

    def rank_hotspots_by_severity(self, hotspot_summary: pd.DataFrame) -> pd.DataFrame:
        """
        Rank hotspots based on severity score calculated from complaint count and average resolution time.

        Args:
            hotspot_summary (pd.DataFrame): Summarized hotspot DataFrame.

        Returns:
            pd.DataFrame: Hotspot summary with severity score and rank.
        """
        if hotspot_summary.empty:
            return hotspot_summary
            
        df = hotspot_summary.copy()
        
        if 'avg_resolution_time' in df.columns:
            median_res_time = df['avg_resolution_time'].median()
            df['avg_resolution_time'] = df['avg_resolution_time'].fillna(median_res_time if pd.notna(median_res_time) else 1.0)
        else:
            df['avg_resolution_time'] = 1.0
            
        scaler = MinMaxScaler()
        
        counts = df[['complaint_count']].values
        norm_counts = scaler.fit_transform(counts) if len(counts) > 0 else np.zeros_like(counts)
        
        times = df[['avg_resolution_time']].values
        norm_times = scaler.fit_transform(times) if len(times) > 0 else np.zeros_like(times)
        
        df['severity_score'] = norm_counts.flatten() * norm_times.flatten()
        df = df.sort_values(by='severity_score', ascending=False).reset_index(drop=True)
        df['severity_rank'] = df.index + 1
        
        return df

