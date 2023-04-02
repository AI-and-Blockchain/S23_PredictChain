import pandas as pd


def load_data(filename: str):
    df = pd.read_csv(filename)
    print(df)
