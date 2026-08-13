import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from utils.helpers import get_sla_threshold

class SLAPredictor:
    """
    Predicts the risk of SLA breaches for civic complaints with feature engineering.
    """

    def __init__(self):
        """Initialize the SLAPredictor."""
        self.model = None
        self.cat_features = ['category', 'ward_name']
        self.num_features = ['complaint_month', 'complaint_dayofweek', 'complaint_hour', 'desc_length', 'sla_threshold_hours']
        self.pipeline = None
        self.is_trained = False

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineers temporal, textual, and domain-specific features."""
        df_ext = df.copy()
        
        # Datetime features
        if 'complaint_date' in df_ext.columns:
            dates = pd.to_datetime(df_ext['complaint_date'], errors='coerce')
            df_ext['complaint_month'] = dates.dt.month.fillna(1)
            df_ext['complaint_dayofweek'] = dates.dt.dayofweek.fillna(0)
            df_ext['complaint_hour'] = dates.dt.hour.fillna(12)
        else:
            df_ext['complaint_month'] = 1
            df_ext['complaint_dayofweek'] = 0
            df_ext['complaint_hour'] = 12

        # Text length feature
        if 'description' in df_ext.columns:
            df_ext['desc_length'] = df_ext['description'].astype(str).str.len()
        else:
            df_ext['desc_length'] = 20

        # Domain SLA threshold feature
        if 'category' in df_ext.columns:
            df_ext['sla_threshold_hours'] = df_ext['category'].apply(lambda c: get_sla_threshold(str(c)))
        else:
            df_ext['sla_threshold_hours'] = 72

        return df_ext

    def prepare_features(self, df: pd.DataFrame, target_col: str = 'sla_breached') -> tuple:
        """
        Prepare features and target for training.

        Args:
            df (pd.DataFrame): Input dataframe.
            target_col (str, optional): Target column name. Defaults to 'sla_breached'.

        Returns:
            tuple: (X, y) feature matrix and target vector.
        """
        df_ext = self.engineer_features(df)
        
        if 'sla_breached' not in df_ext.columns:
            def calculate_breach(row):
                if row.get('status') == 'Resolved' and pd.notna(row.get('resolution_time_hours')):
                    category = row.get('category')
                    threshold = get_sla_threshold(str(category)) if category else 72
                    return 1 if row['resolution_time_hours'] > threshold else 0
                return np.nan
                
            df_ext['sla_breached'] = df_ext.apply(calculate_breach, axis=1)
            
        train_df = df_ext.dropna(subset=['sla_breached'])
        
        X = train_df[self.cat_features + self.num_features]
        y = train_df[target_col].astype(int)
        
        return X, y

    def train(self, df: pd.DataFrame, feature_cols: list = None, target_col: str = 'sla_breached') -> dict:
        """
        Train the optimized SLA breach prediction model.

        Args:
            df (pd.DataFrame): Training data.
            feature_cols (list, optional): Ignored if using engineered features.
            target_col (str, optional): Target column. Defaults to 'sla_breached'.

        Returns:
            dict: Evaluation metrics and feature importances.
        """
        X, y = self.prepare_features(df, target_col)
        
        # Build composite Pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), self.cat_features),
                ('num', Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler())
                ]), self.num_features)
            ]
        )
        
        self.pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                min_samples_split=4,
                random_state=42,
                class_weight='balanced'
            ))
        ])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        
        # Fit model
        self.pipeline.fit(X_train, y_train)
        
        # Predict on test
        y_pred = self.pipeline.predict(X_test)
        
        # Compute metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Feature importances extraction
        rf = self.pipeline.named_steps['classifier']
        cat_encoder = self.pipeline.named_steps['preprocessor'].named_transformers_['cat']
        encoded_cat_names = list(cat_encoder.get_feature_names_out(self.cat_features))
        all_feature_names = encoded_cat_names + self.num_features
        
        importances = rf.feature_importances_
        feature_importance_dict = dict(zip(all_feature_names, importances))
        
        sorted_importances = dict(sorted(feature_importance_dict.items(), key=lambda item: item[1], reverse=True)[:10])
        
        self.is_trained = True
        
        return {
            'accuracy': float(acc),
            'precision': float(prec),
            'recall': float(rec),
            'f1': float(f1),
            'feature_importances': sorted_importances,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }

    def predict_breach_risk(self, df: pd.DataFrame, feature_cols: list = None) -> pd.DataFrame:
        """
        Predict breach risk for open complaints using engineered features.

        Args:
            df (pd.DataFrame): Input dataframe containing complaints.
            feature_cols (list, optional): Ignored.

        Returns:
            pd.DataFrame: Open complaints augmented with breach probabilities and flags.
        """
        if not self.is_trained:
            raise ValueError('Model not trained yet')
            
        df_ext = self.engineer_features(df)
        open_df = df_ext[df_ext.get('status') == 'Open'].copy()
        
        if open_df.empty:
            return pd.DataFrame()
            
        X = open_df[self.cat_features + self.num_features]
        probabilities = self.pipeline.predict_proba(X)
        
        open_df['breach_probability'] = probabilities[:, 1] if probabilities.shape[1] > 1 else 0
        
        def assign_risk_flag(prob):
            if prob >= 0.7:
                return 'High Risk'
            elif prob >= 0.4:
                return 'Medium Risk'
            else:
                return 'Low Risk'
                
        open_df['breach_flag'] = open_df['breach_probability'].apply(assign_risk_flag)
        
        return open_df

    def generate_priority_action(self, row: pd.Series) -> str:
        """
        Generate a priority action based on breach probability and category.

        Args:
            row (pd.Series): A row from the predictions dataframe.

        Returns:
            str: Suggested priority action.
        """
        prob = row.get('breach_probability', 0)
        category = row.get('category', '')
        
        if pd.isna(category) or not isinstance(category, str):
            category_str = str(category).lower()
        else:
            category_str = category.lower()
            
        if prob >= 0.7:
            return f'ESCALATE IMMEDIATELY: High breach risk for {category}. Deploy emergency crew.'
        elif prob >= 0.4:
            if 'pothole' in category_str:
                return 'Schedule road repair crew within 48 hours'
            elif 'garbage' in category_str:
                return 'Dispatch sanitation team urgently'
            elif 'streetlight' in category_str:
                return 'Assign electrical maintenance team'
            elif 'water_leakage' in category_str:
                return 'Send plumbing repair unit'
            elif 'drainage' in category_str:
                return 'Deploy drainage cleaning squad'
            else:
                return 'Review and assign to appropriate department'
        else:
            return 'Monitor: Currently within expected SLA timeline.'
