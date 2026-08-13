import pandas as pd
import os

class DataProfiler:
    """Class for generating data profiling reports."""

    def generate_profile_report(self, df: pd.DataFrame, output_path: str = 'report.html') -> str:
        """Generates an HTML profile report for a DataFrame with a graceful fallback."""
        try:
            from ydata_profiling import ProfileReport
            profile = ProfileReport(df, minimal=True, title="Data Profiling Report")
            profile.to_file(output_path)
            return output_path
        except ImportError:
            # Fallback manual profiling
            return self._generate_fallback_report(df, output_path)
        except Exception as e:
            # Catching other errors and falling back
            return self._generate_fallback_report(df, output_path)

    def _generate_fallback_report(self, df: pd.DataFrame, output_path: str) -> str:
        """Generates a simple HTML report manually if ydata-profiling is unavailable."""
        
        describe_html = df.describe(include='all').to_html(classes='table table-striped table-bordered')
        dtypes_html = pd.DataFrame(df.dtypes, columns=['Data Type']).to_html(classes='table table-striped table-bordered')
        missing_html = pd.DataFrame(df.isnull().sum(), columns=['Missing Values']).to_html(classes='table table-striped table-bordered')
        
        html_content = f"""
        <html>
        <head>
            <title>Fallback Data Profiling Report</title>
            <style>
                body {{ font-family: sans-serif; padding: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #555; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; color: #333; }}
            </style>
        </head>
        <body>
            <h1>Data Profiling Report (Fallback Mode)</h1>
            <p>ydata-profiling was not available or failed to run, showing basic statistics.</p>
            
            <h2>Data Types</h2>
            {dtypes_html}
            
            <h2>Missing Values</h2>
            {missing_html}
            
            <h2>Descriptive Statistics</h2>
            {describe_html}
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return output_path
