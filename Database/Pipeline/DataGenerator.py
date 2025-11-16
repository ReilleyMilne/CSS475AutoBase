import csv
import io
import os
import random
import subprocess
import hashlib

class DataGenerator:
    def __init__(self, db_config, api_key, schemas, csv_input_dir, generated_sql_data_dir):
        self.db_name = db_config['database']
        self.schemas = schemas
        self.csv_input_dir = csv_input_dir
        self.generated_sql_data_dir = generated_sql_data_dir
        self.api_key = api_key


    def fetch_mockaroo_csv(self, schema_id: str, count: int, api_key: str) -> str:
        url = f"https://api.mockaroo.com/api/{schema_id}?count={count}&key={api_key}"
        curl_command = ["curl", url]

        result = subprocess.run(curl_command, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"cURL error: {result.stderr.decode()}")

        return result.stdout.decode()


    def csv_to_sql(self, csv_content: str, table_name: str) -> str:
        sql_lines = [f"USE `{self.db_name}`;\n"]
        f = io.StringIO(csv_content)
        reader = csv.reader(f)
        
        headers = next(reader)
        
        for row in reader:
            row_escaped = [val.replace("'", "''") for val in row]
            values = ", ".join(f"'{val}'" for val in row_escaped)
            sql_lines.append(f"INSERT INTO `{table_name}` ({', '.join(headers)}) VALUES ({values});")
        
        sql_data = "\n".join(sql_lines)
        return sql_data


    def inject_foreign_keys(self, csv_data: str, saved_columns: dict) -> str:
        f = io.StringIO(csv_data)
        reader = csv.reader(f)
        
        headers = next(reader)
        rows = list(reader)

        for col_idx, col_name in enumerate(headers):
            if col_name in saved_columns:
                fk_values = saved_columns[col_name]
                if not fk_values:
                    raise ValueError(f"No saved values found for foreign key column '{col_name}'")

                for row in rows:
                    rand_choice = random.choice(fk_values)
                    row[col_idx] = rand_choice

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        
        return output.getvalue()


    def get_csv_columns(self, csv_data: str) -> list:
        f = io.StringIO(csv_data)
        reader = csv.reader(f)
        headers = next(reader)
        return headers


    def get_column_values_from_csv(self, csv_data: str, column_name: str) -> list:
        f = io.StringIO(csv_data)
        reader = csv.reader(f)
        
        headers = next(reader)
        if column_name not in headers:
            raise ValueError(f"Column '{column_name}' not found in CSV")
        col_index = headers.index(column_name)
        
        values = [row[col_index] for row in reader]
        return values


    def generate_auth_inserts(self, table_name: str, id_col: str, ids: list, names: list):
        if len(ids) != len(names):
            raise ValueError("Length of IDs and Names must match.")

        os.makedirs(self.generated_sql_data_dir, exist_ok=True)

        auth_table_name = f"{table_name}Auth"
        insert_statements = []

        for pk_val, name in zip(ids, names):
            username = name.replace(" ", "").lower() + ".username"
            random_password = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10))
            password_hash = hashlib.sha256(random_password.encode()).hexdigest()

            insert_sql = (
                f"INSERT INTO {auth_table_name} ({id_col}, Username, PasswordHash) "
                f"VALUES ({pk_val}, `{username}`, `{password_hash}`);"
            )
            insert_statements.append(insert_sql)

        sql_script = "\n".join(insert_statements)

        file_path = os.path.join(self.generated_sql_data_dir, f"MOCK_{auth_table_name}_DATA.sql")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sql_script)

        print(f"Created auth inserts for {table_name} → {file_path}")


    def fetch_all_schemas(self, count: int = 1000):
        os.makedirs(self.generated_sql_data_dir, exist_ok=True)

        saved_columns = {}

        for table_name, (schema_id, keys) in self.schemas.items():
            print(f"Fetching {count} rows for {table_name}...")
            csv_data = self.fetch_mockaroo_csv(schema_id, count, self.api_key)
            csv_columns = self.get_csv_columns(csv_data)

            if table_name not in saved_columns:
                saved_columns[table_name] = {}

            for key in keys:
                if key in csv_columns:
                    saved_columns[table_name][key] = self.get_column_values_from_csv(csv_data, key)

            fk_sources = {
                col: values
                for tbl_data in saved_columns.values()
                for col, values in tbl_data.items()
            }

            fk_cols_to_inject = [col for col in csv_columns if col in fk_sources]
            if fk_cols_to_inject:
                csv_data = self.inject_foreign_keys(csv_data, {col: fk_sources[col] for col in fk_cols_to_inject})

            sql_data = self.csv_to_sql(csv_data, table_name)
            file_path = os.path.join(self.generated_sql_data_dir, f"MOCK_{table_name}_DATA.sql")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sql_data)

            print(f"Saved {table_name} data to {file_path}\n")
        
        if (
            "Employee" in saved_columns 
            and saved_columns["Employee"].get("EmployeeID") 
            and saved_columns["Employee"].get("Name")
            and len(saved_columns["Employee"]["EmployeeID"]) > 0
            and len(saved_columns["Employee"]["Name"]) > 0):
            self.generate_auth_inserts("Employee", "EmployeeID", saved_columns["Employee"]["EmployeeID"], saved_columns["Employee"]["Name"])
        else:
            raise ValueError("Employee table data is empty or missing required columns.")
        if (
            "Customer" in saved_columns 
            and saved_columns["Customer"].get("CustomerID") 
            and saved_columns["Customer"].get("Name")
            and len(saved_columns["Customer"]["CustomerID"]) > 0
            and len(saved_columns["Customer"]["Name"]) > 0):
            self.generate_auth_inserts("Customer", "CustomerID", saved_columns["Customer"]["CustomerID"], saved_columns["Customer"]["Name"])
        else:
            raise ValueError("Customer table data is empty or missing required columns.")


    def convert_csv_to_sql(self, table_name):
        filename = f"{table_name}.csv"
        input_file_path = os.path.join(self.csv_input_dir, filename)
        if os.path.exists(input_file_path):
            print(f"Converted data from {filename}...")

            sql_data = None
            with open(input_file_path, "r", encoding="utf-8") as f:
                csv_content = f.read()
                sql_data = self.csv_to_sql(csv_content, table_name)

            output_file_path = os.path.join(self.generated_sql_data_dir, f"MOCK_{table_name}_DATA.sql")
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(sql_data)

            print(f"Converted {filename} successfully.\n")
        else:
            print(f"Warning: {filename} not found in {self.csv_input_dir}.")


    def existing_csv_to_sql(self):
        # Get all files. Remove when we go through first pass.
        file_list = []
        for entry in os.listdir(self.csv_input_dir):
            full_path = os.path.join(self.csv_input_dir, entry)
            if os.path.isfile(full_path):
                entry_name = os.path.splitext(entry)[0]
                entry_ext = os.path.splitext(entry)[1]
                if entry_ext == '.csv':
                    file_list.append(entry_name)

        for table_name in self.schemas.keys():
            self.convert_csv_to_sql(table_name)
            file_list.remove(table_name)
        
        for table_name in file_list:
            self.convert_csv_to_sql(table_name)
