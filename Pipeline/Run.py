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
    'port': 3306
}

# table_name, (schema_id, primary_key)
mockaroo_schemas = {
    "Vehicle": ("eb692b70", "VIN"),
    "Employee": ("66c9b870", "EmployeeID"),
    "Part": ("ae8c9bb0", "PartID"),
    "Customer": ("b9190230", "CustomerID"),
    "SalesOrder": ("ea27b3a0", "SalesOrderID"),
    "ServiceOrder": ("5989a7f0", "ServiceOrderID"),
    "ServiceLine": ("d18caae0", "ServiceLineID")
}

sql_generated_data_path = "MockData"

if __name__ == "__main__":
    dg = DataGenerator(db_config, mockaroo_schemas, sql_generated_data_path)
    di = DataInserter(db_config, mockaroo_schemas, sql_generated_data_path)
    dg.generate_data(1000)
    di.insert_data()
