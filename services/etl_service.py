import os
import json
import logging
import pandas as pd
from datetime import datetime
from database.db_manager import DBManager
from services.api_service import APIService

logger = logging.getLogger(__name__)

class ETLService:
    """
    ETL (Extract, Transform, Load) Pipeline implementation.
    Reads CSV, Excel, JSON and API sources, cleans & merges them,
    and loads them into SQLite tables.
    """
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.api_service = APIService()
        self.source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def run_pipeline(self) -> dict:
        """
        Runs the full ETL pipeline.
        Returns a summary dictionary of records processed.
        """
        summary = {}
        try:
            self.db.log_action("SYSTEM", "ETL_START", "Starting ETL pipeline execution")
            
            # 1. Extract, Clean, and Load Revenue
            summary['revenue'] = self._etl_revenue()
            
            # 2. Extract, Clean, and Load Employees
            summary['employees'] = self._etl_employees()
            
            # 3. Extract, Clean, and Load Clients
            summary['clients'] = self._etl_clients()
            
            # 4. Extract, Clean, and Load Partners (Blended CSV + Excel)
            summary['partners'] = self._etl_partners()
            
            # 5. Extract, Clean, and Load Projects (Blended CSV + JSON)
            summary['projects'] = self._etl_projects()
            
            # 6. Extract and Load API Metrics
            summary['api_metrics'] = self._etl_api_metrics()
            
            self.db.log_action("SYSTEM", "ETL_SUCCESS", f"ETL completed successfully: {json.dumps(summary)}")
            logger.info("ETL pipeline executed successfully.")
            return {"status": "SUCCESS", "summary": summary}
            
        except Exception as e:
            error_msg = f"ETL failed: {str(e)}"
            self.db.log_action("SYSTEM", "ETL_FAILED", error_msg)
            logger.exception("ETL pipeline execution failed.")
            return {"status": "FAILED", "error": error_msg}

    def _etl_revenue(self) -> int:
        """Processes revenue data."""
        csv_path = os.path.join(self.source_dir, "revenue.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Missing revenue.csv at {csv_path}")
            
        df = pd.read_csv(csv_path)
        # Clean: strip whitespace, capitalize headers
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Ensure correct datatypes
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0.0)
        df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0.0)
        
        # Write to SQLite
        self.db.insert_dataframe(df, "revenue", mode="replace")
        return len(df)

    def _etl_employees(self) -> int:
        """Processes employees data."""
        csv_path = os.path.join(self.source_dir, "employees.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Missing employees.csv at {csv_path}")
            
        df = pd.read_csv(csv_path)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Standardize strings
        df['name'] = df['name'].str.strip()
        df['department'] = df['department'].str.strip()
        df['status'] = df['status'].str.strip()
        
        # Normalize join_date
        df['join_date'] = pd.to_datetime(df['join_date']).dt.strftime('%Y-%m-%d')
        df['utilization_pct'] = pd.to_numeric(df['utilization_pct'], errors='coerce').fillna(0).astype(int)
        
        self.db.insert_dataframe(df, "employees", mode="replace")
        return len(df)

    def _etl_clients(self) -> int:
        """Processes clients data."""
        csv_path = os.path.join(self.source_dir, "clients.csv")
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Missing clients.csv at {csv_path}")
            
        df = pd.read_csv(csv_path)
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Clean
        df['client_name'] = df['client_name'].str.strip()
        df['retention_status'] = df['retention_status'].str.strip()
        df['nps'] = pd.to_numeric(df['nps'], errors='coerce').fillna(0).astype(int)
        df['csat'] = pd.to_numeric(df['csat'], errors='coerce').fillna(0.0)
        
        self.db.insert_dataframe(df, "clients", mode="replace")
        return len(df)

    def _etl_partners(self) -> int:
        """Blends CSV and Excel to process partners data."""
        csv_path = os.path.join(self.source_dir, "partners.csv")
        excel_path = os.path.join(self.source_dir, "data", "partner_goals.xlsx")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Missing partners.csv at {csv_path}")
            
        df_csv = pd.read_csv(csv_path)
        df_csv.columns = [c.strip().lower() for c in df_csv.columns]
        df_csv['partner_name'] = df_csv['partner_name'].str.strip()
        df_csv['status'] = df_csv['status'].str.strip()
        df_csv['pipeline_value'] = pd.to_numeric(df_csv['pipeline_value'], errors='coerce').fillna(0.0)

        # Merge with Excel goals if available
        if os.path.exists(excel_path):
            try:
                df_excel = pd.read_excel(excel_path)
                df_excel.columns = [c.strip().lower() for c in df_excel.columns]
                df_excel['partner_name'] = df_excel['partner_name'].str.strip()
                
                df_merged = pd.merge(df_csv, df_excel, on='partner_name', how='left')
            except Exception as e:
                logger.warning(f"Failed to load/merge Excel file. Proceeding with CSV only. Error: {e}")
                df_merged = df_csv.copy()
                df_merged['target_pipeline'] = 0.0
                df_merged['partner_manager'] = 'Unassigned'
                df_merged['contract_date'] = None
        else:
            df_merged = df_csv.copy()
            df_merged['target_pipeline'] = 0.0
            df_merged['partner_manager'] = 'Unassigned'
            df_merged['contract_date'] = None
            
        df_merged['target_pipeline'] = pd.to_numeric(df_merged['target_pipeline'], errors='coerce').fillna(0.0)
        
        self.db.insert_dataframe(df_merged, "partners", mode="replace")
        return len(df_merged)

    def _etl_projects(self) -> int:
        """Blends CSV and JSON to process projects data."""
        csv_path = os.path.join(self.source_dir, "projects.csv")
        json_path = os.path.join(self.source_dir, "data", "project_details.json")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Missing projects.csv at {csv_path}")
            
        df_csv = pd.read_csv(csv_path)
        df_csv.columns = [c.strip().lower() for c in df_csv.columns]
        df_csv['project_id'] = df_csv['project_id'].str.strip()
        df_csv['project_name'] = df_csv['project_name'].str.strip()
        df_csv['status'] = df_csv['status'].str.strip()
        df_csv['budget'] = pd.to_numeric(df_csv['budget'], errors='coerce').fillna(0.0)
        df_csv['completion_pct'] = pd.to_numeric(df_csv['completion_pct'], errors='coerce').fillna(0).astype(int)
        df_csv['delay_days'] = pd.to_numeric(df_csv['delay_days'], errors='coerce').fillna(0).astype(int)
        
        # Merge with JSON project details
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                df_json = pd.DataFrame(json_data)
                df_json.columns = [c.strip().lower() for c in df_json.columns]
                df_json['project_id'] = df_json['project_id'].str.strip()
                
                df_merged = pd.merge(df_csv, df_json, on='project_id', how='left')
            except Exception as e:
                logger.warning(f"Failed to read/merge JSON details. Proceeding with CSV only. Error: {e}")
                df_merged = df_csv.copy()
                df_merged['description'] = 'No description available.'
                df_merged['client_name'] = 'N/A'
        else:
            df_merged = df_csv.copy()
            df_merged['description'] = 'No description available.'
            df_merged['client_name'] = 'N/A'

        self.db.insert_dataframe(df_merged, "projects", mode="replace")
        return len(df_merged)

    def _etl_api_metrics(self) -> int:
        """Fetches and stores external API indicators."""
        metrics = self.api_service.fetch_market_metrics()
        rows = []
        last_updated = datetime.now().isoformat()
        
        for k, v in metrics.items():
            rows.append({
                "metric_name": k,
                "metric_value": float(v),
                "last_updated": last_updated
            })
            
        df = pd.DataFrame(rows)
        self.db.insert_dataframe(df, "api_metrics", mode="replace")
        return len(df)
