from sqlalchemy import MetaData, inspect
from database import engine

def inspect_tables_with_columns(schema_name):
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema=schema_name)
        print(f"Tables and their columns in the schema '{schema_name}':")
        for table_name in tables:
            print(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name, schema=schema_name)
            for column in columns:
                print(f"  - {column['name']} ({column['type']})")
    except Exception as e:
        print(f"Error inspecting tables: {e}")

if __name__ == "__main__":
    schema_to_filter = "ia"  # Your schema name
    inspect_tables_with_columns(schema_to_filter)
