import os
import sketch
os.environ["SKETCH_MAX_COLUMNS"] = "50"

def get_sketch_ask_data_summary(df, question = "What is this data set about"):
    df = df.iloc[:, :49]
    return df.sketch.ask(question, call_display=False)

def get_sketch_ask_data_column_definition(df, question = "Provide a short friendly name and description for each column, and deliver as an HTML list"):
    df = df.iloc[:, :49]
    return df.sketch.ask(question, call_display=False)

# df_extract_inventory.sketch.ask("What is this data set about")
# import inspect
# inspect.signature(df_extract_inventory.sketch.ask)
# data_summary = get_sketch_ask_data_summary(df_extract_inventory_abbrev, "What is this data set about?")
# print(data_summary)
# from IPython.display import display, HTML
# df_column_descriptions_html = get_sketch_ask_data_column_definition(df_extract_inventory, call_display=False)
# display(HTML(df_column_descriptions_html))

import pandas as pd
import re

def clean_sketch_response(text):
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\u2028', ' ')
    return text

def get_column_descriptions_simple(df, show_work = False):
    rows = []
    for i, col in enumerate(df.columns, start=1):
        question = f"What is one brief sentence meaning of the {col} column? do not use special characters, line feeds, or quotes"
        desc_raw = df.head(10)[[col]].sketch.ask(question, call_display=False)
        desc = clean_sketch_response(desc_raw)
        if show_work:
            print(f"Raw: {desc_raw} | Cleaned: {desc}")
        rows.append({
            "column_number": i,
            "column_name": col,
            "column_description": desc
        })
    return pd.DataFrame(rows)
