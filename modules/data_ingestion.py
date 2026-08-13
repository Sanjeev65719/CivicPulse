import pandas as pd
import requests
import json
import os
import streamlit as st

class DataIngestion:
    """Class to handle data ingestion from various sources."""
    
    def load_file(self, uploaded_file) -> pd.DataFrame:
        """Reads CSV or XLSX files into a pandas DataFrame."""
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            return pd.read_excel(uploaded_file)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or XLSX files.")

    def load_from_api(self, url: str, api_key: str = None, headers_json: str = None) -> pd.DataFrame:
        """Fetches data from an API and parses JSON into a DataFrame."""
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        if headers_json:
            try:
                headers.update(json.loads(headers_json))
            except json.JSONDecodeError:
                pass # ignore invalid JSON
                
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)

    @staticmethod
    @st.cache_data(show_spinner="Loading sample dataset...")
    def load_sample_data() -> pd.DataFrame:
        """Loads a sample dataset with caching for fast UI reruns."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'civic_complaints_sample.csv')
        return pd.read_csv(file_path)
