import pandas as pd
from sqlalchemy import create_engine, inspect, text
import traceback

class DatabaseManager:
    """Manages SQLite database connections and indexed operations."""

    def __init__(self, db_path: str = 'civicpulse.db'):
        """Initializes database connection."""
        self.engine = create_engine(f'sqlite:///{db_path}', connect_args={'check_same_thread': False})

    def create_indexes(self, table_name: str = 'complaints') -> None:
        """Creates database indexes for fast query execution."""
        index_queries = [
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_category ON {table_name}(category);",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_ward ON {table_name}(ward_name);",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_status ON {table_name}(status);",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_complaint_id ON {table_name}(complaint_id);"
        ]
        with self.engine.begin() as connection:
            for q in index_queries:
                try:
                    connection.execute(text(q))
                except Exception as e:
                    pass

    def save_dataframe(self, df: pd.DataFrame, table_name: str = 'complaints') -> None:
        """Saves a DataFrame to the database and builds performance indexes."""
        with self.engine.begin() as connection:
            df.to_sql(table_name, con=connection, if_exists='replace', index=False)
        self.create_indexes(table_name)

    def execute_query(self, sql: str) -> pd.DataFrame:
        """Executes an SQL query and returns results as DataFrame."""
        try:
            with self.engine.connect() as connection:
                return pd.read_sql(sql, connection)
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()

    def get_database_info(self) -> dict:
        """Retrieves information about database tables and columns."""
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        
        info = {'table_names': table_names}
        for table in table_names:
            columns = [col['name'] for col in inspector.get_columns(table)]
            
            try:
                with self.engine.connect() as connection:
                    row_count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", connection)['count'].iloc[0]
            except Exception:
                row_count = 0
                
            info[table] = {
                'column_names': columns,
                'row_count': int(row_count)
            }
            
        return info

