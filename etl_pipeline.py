import sys
import os
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ETL_Pipeline_Runner")

# Add the project directory to path to ensure modules resolve correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.db_manager import DBManager
from services.etl_service import ETLService

def run_etl():
    logger.info("Initializing DB Manager...")
    db_manager = DBManager()
    
    logger.info("Starting ETL Ingestion and Processing Pipeline...")
    etl_service = ETLService(db_manager)
    result = etl_service.run_pipeline()
    
    if result["status"] == "SUCCESS":
        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"Ingested Record Counts: {result['summary']}")
        print("\n=== ETL Pipeline Execution Success ===")
        for key, val in result['summary'].items():
            print(f"- Table '{key}': {val} records processed.")
        print("======================================\n")
        return 0
    else:
        logger.error(f"ETL PIPELINE FAILED! Error: {result.get('error')}")
        print(f"\n!!! ETL Pipeline Execution Failed: {result.get('error')} !!!\n")
        return 1

if __name__ == '__main__':
    sys.exit(run_etl())
