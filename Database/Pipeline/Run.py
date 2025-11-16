from DataGenerator import DataGenerator
from DataInserter import DataInserter

import os
from dotenv import load_dotenv

load_dotenv()
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': 3306,
}
mockaroo_api_key = os.getenv('MOCKAROO_API_KEY')

# table_name, (schema_id, primary_key)
mockaroo_schemas = {
    "Vehicle": ("eb692b70", ["VIN"]),
    "Employee": ("66c9b870", ["EmployeeID", "Name"]),
    "Part": ("ae8c9bb0", ["PartID"]),
    "Customer": ("b9190230", ["CustomerID", "Name"]),
    "SalesOrder": ("ea27b3a0", ["SalesOrderID"]),
    "ServiceOrder": ("5989a7f0", ["ServiceOrderID"]),
    "ServiceLine": ("d18caae0", ["ServiceLineID"]),
    "EmployeeAuth": ("", []),
    "CustomerAuth": ("", [])
}

csv_input_dir = "./Database/AutoBase"
generated_sql_data_dir = "./Database/MockData"

if __name__ == "__main__":
    dg = DataGenerator(db_config, mockaroo_schemas, csv_input_dir, generated_sql_data_dir, mockaroo_api_key=mockaroo_api_key)
    di = DataInserter(db_config, mockaroo_schemas, generated_sql_data_dir)
    
    # Only use 'dg.fetch_all_schemas' if generated from Mockaroo.
    # However, Mockaroo typically generates duplicate data when we need unique data.
    # So we just generate data on Fabricate.tonic.ai and upload it into AutoBase
    # dg.fetch_all_schemas(1000)

    dg.existing_csv_to_sql()
    di.insert_data()
