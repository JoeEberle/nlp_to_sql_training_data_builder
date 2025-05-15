import os
import sketch
import json 

def generate_table_schema_json(table_name, table_description, df_sample_data, df_column_descriptions, output_file=None):
    """
    Generates a JSON file describing a table schema for SQL/NLP training.

    Parameters:
        table_name (str): Name of the table
        table_description (str): Short description of the table's purpose
        df_sample_data (pd.DataFrame): The sample data (not used, but useful for checks)
        df_column_descriptions (pd.DataFrame): Must have 'column_name' and 'column_description'
        output_file (str, optional): If provided, the JSON will be saved to this file
    """
    # Build column list
    columns_json = []
    for _, row in df_column_descriptions.iterrows():
        column_name = row['column_name']
        column_description = row['column_description']
        column_type = str(df_sample_data[column_name].dtype).upper()

        # Simplify pandas dtypes to general SQL types
        if 'int' in column_type:
            column_type = 'INTEGER'
        elif 'float' in column_type:
            column_type = 'FLOAT'
        elif 'bool' in column_type:
            column_type = 'BOOLEAN'
        elif 'date' in column_type or 'datetime' in column_type:
            column_type = 'DATE'
        else:
            column_type = 'TEXT'

        columns_json.append({
            "name": column_name,
            "type": column_type,
            "description": column_description
        })

    # Assemble final JSON object
    table_json = {
        "table": table_name,
        "description": table_description,
        "columns": columns_json
    }

    # Save to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(table_json, f, indent=2, ensure_ascii=False)

    return table_json




import re

def validate_schema_json(schema_json, suggest_types=False):
    errors = []
    warnings = []
    suggestions = []

    # Top-level structure
    required_top_keys = {"table", "description", "columns"}
    actual_top_keys = set(schema_json.keys())
    missing_keys = required_top_keys - actual_top_keys
    if missing_keys:
        errors.append(f"Missing top-level keys: {missing_keys}")

    # Check basic field content
    if not schema_json.get("table"):
        errors.append("Missing or empty 'table' name.")
    if not schema_json.get("description") or len(schema_json["description"].strip()) < 10:
        warnings.append("Table description is very short or missing.")

    # Check columns
    columns = schema_json.get("columns", [])
    if not isinstance(columns, list) or len(columns) == 0:
        errors.append("No columns provided or 'columns' is not a list.")

    seen_names = set()
    for i, col in enumerate(columns):
        prefix = f"Column #{i+1} ({col.get('name', '?')}):"

        # Validate structure
        for field in ["name", "type", "description"]:
            if field not in col:
                errors.append(f"{prefix} Missing field '{field}'.")

        # Check emptiness or bad formatting
        name = col.get("name", "")
        if not name:
            errors.append(f"{prefix} Column name is empty.")
        elif name in seen_names:
            errors.append(f"{prefix} Duplicate column name '{name}'.")
        seen_names.add(name)

        desc = col.get("description", "").strip()
        if not desc or len(desc) < 10:
            warnings.append(f"{prefix} Description is too short or missing.")
        elif re.search(r"[\n\"']", desc):
            warnings.append(f"{prefix} Description contains disallowed characters (newline, quote).")

        dtype = col.get("type", "").upper()
        valid_types = {"INTEGER", "FLOAT", "TEXT", "BOOLEAN", "DATE", "UUID", "VARCHAR"}
        if dtype not in valid_types:
            warnings.append(f"{prefix} Unrecognized or non-standard SQL type: '{dtype}'.")

        # Suggest better types if enabled
        if suggest_types and dtype == "TEXT":
            if re.search(r"(?i)id|number", name):
                suggestions.append(f"{prefix} Consider changing type to 'INTEGER' or 'UUID'.")
            elif re.search(r"(?i)date|time", name):
                suggestions.append(f"{prefix} Consider changing type to 'DATE'.")
            elif re.search(r"(?i)is_|has_|flag|status", name):
                suggestions.append(f"{prefix} Consider changing type to 'BOOLEAN'.")

    # Final output
    return {
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "is_valid": len(errors) == 0
    }
