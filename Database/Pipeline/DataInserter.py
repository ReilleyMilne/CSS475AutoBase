import mysql.connector
import os

class DataInserter:
    def __init__(self, db_config, schemas, input_dir):
        self.db_config = db_config
        self.schemas = schemas
        self.input_dir = input_dir
        self.conn = None
        self.cursor = None


    def execute_sql_file(self, cursor, sql_file_path):
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_commands = f.read()
        for cmd in sql_commands.split(";"):
            cmd = cmd.strip()
            if cmd:
                cursor.execute(cmd)


    def insert_sql_file(self, table_name):
        filename = f"MOCK_{table_name}_DATA.sql"
        file_path = os.path.join(self.input_dir, filename)
        if os.path.exists(file_path):
            print(f"Inserting data from {filename}...")
            self.execute_sql_file(self.cursor, file_path)
            self.conn.commit()
            print(f"Inserted {filename} successfully.\n")
        else:
            print(f"Warning: {filename} not found in {self.input_dir}.")

    def insert_data(self):
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()

        file_list = []
        for entry in os.listdir(self.input_dir):
            full_path = os.path.join(self.input_dir, entry)
            if os.path.isfile(full_path):
                entry_name = os.path.splitext(entry)[0]
                entry_ext = os.path.splitext(entry)[1]
                if entry_ext == '.sql':
                    file_list.append(entry_name)

        # Insert files in the order specified by schemas first
        for table_name in self.schemas.keys():
            self.insert_sql_file(table_name)
            formatted_table_name = 'MOCK_' + table_name + '_DATA'
            file_list.remove(formatted_table_name)

        for file_name in file_list:
            table_name = file_name.split('_')[1]
            self.insert_sql_file(table_name)

        # Then insert the rest of the files not in schema
        self.cursor.close()
        self.conn.close()
