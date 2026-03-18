import pandas as pd


def extract_csv(file_path):
    
    df = pd.read_csv(file_path)

    records = df.to_dict(orient="records")

    return records