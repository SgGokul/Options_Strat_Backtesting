from data_processing import groupby_fut
import pandas as pd

## extract type I future contracts and store its ohlc datas in a single dataframe
def bnf_data(fut_data: pd.DataFrame) -> pd.DataFrame:
    bnf_dict = {}
    bnf_dict = groupby_fut(fut_data)

    keys_with_I = [key for key in bnf_dict.keys() if 'I' in key and 'II' not in key and 'III' not in key]

    dfs = [bnf_dict[key] for key in keys_with_I]
    df = pd.concat(dfs, ignore_index=True)
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%Y-%m-%d %H:%M:%S')
    
    return df