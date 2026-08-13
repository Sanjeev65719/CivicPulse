import pandas as pd
import numpy as np

class DataCleaning:
    """Class for cleaning and validating complaint data."""

    def assess_data_quality(self, df: pd.DataFrame) -> dict:
        """Assess the quality of the given DataFrame."""
        total_rows = len(df)
        
        missing_percentage = (df.isnull().sum() / total_rows * 100).to_dict() if total_rows > 0 else {}
        duplicate_count = df.duplicated().sum()
        dtype_summary = df.dtypes.astype(str).to_dict()
        
        invalid_coordinates_count = 0
        if 'latitude' in df.columns and 'longitude' in df.columns:
            invalid_coords = df[
                (df['latitude'] < 0) | (df['latitude'] > 90) |
                (df['longitude'] < -180) | (df['longitude'] > 180)
            ]
            invalid_coordinates_count = len(invalid_coords)
            
        return {
            'missing_percentage': missing_percentage,
            'duplicate_count': int(duplicate_count),
            'dtype_summary': dtype_summary,
            'total_rows': total_rows,
            'total_columns': len(df.columns),
            'invalid_coordinates_count': int(invalid_coordinates_count)
        }

    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
        """Handles missing values in the DataFrame."""
        df_clean = df.copy()
        if strategy == 'drop':
            df_clean = df_clean.dropna()
        elif strategy == 'fill_mean':
            for col in df_clean.select_dtypes(include=[np.number]).columns:
                df_clean[col].fillna(df_clean[col].mean(), inplace=True)
        elif strategy == 'fill_mode':
            for col in df_clean.select_dtypes(include=['object', 'category']).columns:
                if not df_clean[col].mode().empty:
                    df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
        return df_clean

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes duplicate rows."""
        return df.drop_duplicates()

    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes column names to lowercase with underscores."""
        df_clean = df.copy()
        df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(' ', '_')
        return df_clean

    def validate_coordinates(self, df: pd.DataFrame, lat_col: str = 'latitude', lon_col: str = 'longitude') -> pd.DataFrame:
        """Flags rows outside Bengaluru bounding box."""
        df_clean = df.copy()
        if lat_col in df_clean.columns and lon_col in df_clean.columns:
            # Bengaluru bounding box: lat 12.5-13.5, lon 77.0-78.5
            valid_lat = df_clean[lat_col].between(12.5, 13.5)
            valid_lon = df_clean[lon_col].between(77.0, 78.5)
            df_clean['coordinates_valid'] = valid_lat & valid_lon
        return df_clean

    def parse_dates(self, df: pd.DataFrame, date_cols: list = None) -> pd.DataFrame:
        """Parses dates and calculates resolution time."""
        df_clean = df.copy()
        if date_cols is None:
            date_cols = ['complaint_date', 'resolved_date']
            
        for col in date_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                
        if 'complaint_date' in df_clean.columns and 'resolved_date' in df_clean.columns:
            time_diff = df_clean['resolved_date'] - df_clean['complaint_date']
            df_clean['resolution_time_hours'] = time_diff.dt.total_seconds() / 3600
            
        return df_clean
