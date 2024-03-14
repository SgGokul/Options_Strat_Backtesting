import pandas as pd

## remove duplicate values from a list
def remove_duplicates(lst):
    seen = set()
    unique_list = []
    
    for item in lst:
        if item not in seen:
            unique_list.append(item)
            seen.add(item)
    
    ## returns a list without any duplicate values        
    return unique_list

## grouping futures data based on contract type and expiry
def groupby_fut(fut_data):
    fut_data['Datetime'] = pd.to_datetime(fut_data['Date'] + ' ' + fut_data['Time'])
    del fut_data['Date'], fut_data['Time']
    
    fut_data = fut_data[['Ticker', 'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'OI', 'Contract', 'Expiry']]
    grouped_data = fut_data.groupby(['Contract', 'Expiry'])
    grouped_dfs = {}

    for group, df in grouped_data:
        contract, expiry = group
        df_name = f"BANKNIFTY_{contract}_{expiry}"
        grouped_dfs[df_name] = df

    ## returns dictionary with key as specified future contract data 
    ## and value as the respective ohlc data
    return grouped_dfs

## grouping options data based on expiry, strike price and contract type
def groupby_options(options_data):
    options_data['Datetime'] = pd.to_datetime(options_data['Date'] + ' ' + options_data['Time'])
    del options_data['Date'], options_data['Time']
    
    grouped_data = options_data.groupby(['Expiry', 'Strike', 'Type'])
    grouped_dfs = {}
    expiry_date = []
    
    
    for group, df in grouped_data:
        expiry, strike, type = group
        df_name = f"BANKNIFTY_{expiry}_{strike}_{type}"
        expiry_date.append(expiry)
        grouped_dfs[df_name] = df
    
    expiry_date = remove_duplicates(expiry_date)    
    
    ## returns 1. dictionary with key as specified option contract data and
    ## value as the ohlc data of premium 2. list containing expiry dates
    return grouped_dfs, expiry_date