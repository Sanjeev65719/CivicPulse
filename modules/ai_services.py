import os
import json
import pandas as pd
import requests

class AIServices:
    """Handles AI integrations and fallback rule-based NLP."""

    def __init__(self):
        self.api_key = os.environ.get('HF_API_KEY')
        self.use_ai = bool(self.api_key)
        self.api_url = 'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2'

    def natural_language_to_sql(self, question: str, schema_info: dict) -> str:
        """Converts natural language questions to SQL queries."""
        question_lower = question.lower()
        
        if self.use_ai:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            prompt = f"Given the database schema: {json.dumps(schema_info)}, generate an SQL query to answer this question: {question}. Return ONLY the SQL query."
            try:
                response = requests.post(self.api_url, headers=headers, json={"inputs": prompt})
                response.raise_for_status()
                generated_text = response.json()[0].get('generated_text', '')
                sql = generated_text.replace(prompt, '').strip()
                if sql:
                    return sql
            except Exception as e:
                print(f"AI Service error: {e}. Falling back to rule-based.")

        # Rule-based fallback
        if 'most complaints' in question_lower or 'highest' in question_lower:
            return "SELECT category, COUNT(*) as count FROM complaints GROUP BY category ORDER BY count DESC"
        elif 'unresolved' in question_lower or 'open' in question_lower or 'pending' in question_lower:
            return "SELECT * FROM complaints WHERE status = 'Open'"
        elif 'ward' in question_lower and 'complaint' in question_lower:
            return "SELECT ward_name, COUNT(*) as count FROM complaints GROUP BY ward_name ORDER BY count DESC"
        elif 'average' in question_lower and ('resolution' in question_lower or 'time' in question_lower):
            return "SELECT category, AVG(resolution_time_hours) as avg_hours FROM complaints WHERE status = 'Resolved' GROUP BY category"
        elif 'breach' in question_lower or 'sla' in question_lower:
            return "SELECT * FROM complaints WHERE sla_breached = 1"
        elif 'recent' in question_lower or 'latest' in question_lower:
            return "SELECT * FROM complaints ORDER BY complaint_date DESC LIMIT 10"
        else:
            return "SELECT * FROM complaints LIMIT 20"

    def generate_insight_summary(self, df: pd.DataFrame) -> str:
        """Generates a text summary of DataFrame statistics."""
        summary = f"Total rows: {len(df)}\n"
        summary += f"Total columns: {len(df.columns)}\n\n"
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary += "Numeric columns stats:\n"
            for col in numeric_cols:
                summary += f"  - {col}: Mean={df[col].mean():.2f}, Min={df[col].min():.2f}, Max={df[col].max():.2f}\n"
        
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            summary += "\nCategory value counts (Top 3):\n"
            for col in cat_cols:
                counts = df[col].value_counts().head(3).to_dict()
                summary += f"  - {col}: {counts}\n"
                
        if self.use_ai:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            prompt = f"Summarize the following data statistics into a concise insight paragraph:\n{summary}"
            try:
                response = requests.post(self.api_url, headers=headers, json={"inputs": prompt})
                response.raise_for_status()
                generated_text = response.json()[0].get('generated_text', '')
                ai_summary = generated_text.replace(prompt, '').strip()
                if ai_summary:
                    return f"--- AI Summary ---\n{ai_summary}\n\n--- Detailed Stats ---\n{summary}"
            except Exception:
                pass
                
        return summary

    def validate_token(self) -> dict:
        """Validates the Hugging Face API token."""
        if not self.use_ai:
            return {'valid': False, 'message': 'No token configured (HF_API_KEY environment variable is not set).'}
            
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get('https://huggingface.co/api/whoami-v2', headers=headers)
            if response.status_code == 200:
                return {'valid': True, 'message': 'Token is valid.'}
            else:
                return {'valid': False, 'message': f'Invalid token. Status code: {response.status_code}'}
        except Exception as e:
            return {'valid': False, 'message': f'Error validating token: {e}'}
