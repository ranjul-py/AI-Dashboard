import pandas as pd
import os

def create_excel_file():
    data = {
        'partner_name': ['Partner A', 'Partner B', 'Partner C', 'Partner D', 'Partner E'],
        'target_pipeline': [3000000, 2000000, 4000000, 1000000, 1000000],
        'partner_manager': ['Sarah Connor', 'John Doe', 'Jane Smith', 'Robert Lee', 'Emily Watson'],
        'contract_date': ['2024-01-10', '2023-11-15', '2024-03-22', '2022-09-01', '2023-05-18']
    }
    
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs('d:/project/data', exist_ok=True)
    
    file_path = 'd:/project/data/partner_goals.xlsx'
    df.to_excel(file_path, index=False)
    print(f"Created Excel file at {file_path}")

if __name__ == '__main__':
    create_excel_file()
