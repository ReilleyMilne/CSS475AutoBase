import mysql.connector
import os

class DataInserter:
    def __init__(self, db_config, schemas, input_dir):
        self.db_config = db_config
        self.schemas = schemas
        self.input_dir = input_dir


    def execute_sql_file(self, cursor, sql_file_path):
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_commands = f.read()
        for cmd in sql_commands.split(";"):
            cmd = cmd.strip()
            if cmd:
                cursor.execute(cmd)


    def insert_data(self):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        # Insert files in the order specified by schemas
        for table_name in self.schemas.keys():
            filename = f"MOCK_{table_name}_DATA.sql"
            file_path = os.path.join(self.input_dir, filename)
            if os.path.exists(file_path):
                print(f"Inserting data from {filename}...")
                self.execute_sql_file(cursor, file_path)
                conn.commit()
                print(f"Inserted {filename} successfully.\n")
            else:
                print(f"Warning: {filename} not found in {self.input_dir}.")
        cursor.close()
        conn.close()
