import csv
import io
import os
import random
import subprocess

class DataGenerator:
    def __init__(self, db_config, schemas, output_dir):
        self.db_name = db_config['database']
        self.schemas = schemas
        self.output_dir = output_dir


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


    def fetch_all_schemas(self, schemas: dict, api_key: str, count: int = 1000, output_dir: str = "MockData"):
        os.makedirs(output_dir, exist_ok=True)

        saved_columns = {}

        for table_name, (schema_id, pk) in schemas.items():
            print(f"Fetching {count} rows for {table_name}...")
            csv_data = self.fetch_mockaroo_csv(schema_id, count, api_key)
            csv_columns = self.get_csv_columns(csv_data)

            # Inject foreign keys only if the saved PK exists
            fk_cols_to_inject = [col for col in csv_columns if col in saved_columns]
            if fk_cols_to_inject:
                csv_data = self.inject_foreign_keys(csv_data, {col: saved_columns[col] for col in fk_cols_to_inject})

            # Save PKs for future FK injection
            if pk in csv_columns:
                saved_columns[pk] = self.get_column_values_from_csv(csv_data, pk)

            sql_data = self.csv_to_sql(csv_data, table_name)

            # Save SQL file
            file_path = os.path.join(output_dir, f"MOCK_{table_name}_DATA.sql")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sql_data)

            print(f"Saved {table_name} data to {file_path}\n")


    def generate_data(self, count):
        api_key = "a8cbd320"
        self.fetch_all_schemas(self.schemas, api_key, count, self.output_dir)