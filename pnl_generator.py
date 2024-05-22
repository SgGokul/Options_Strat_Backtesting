import math
import pandas as pd

def calculate_margin_and_capital(df: pd.DataFrame, lot_size: int, capital: float, capital_allocation_per_trade: float) -> None:
    ## iterating through rows of the tradebook to calculate PnL and Capital
    for index, row in df.iterrows():
        ## calcualte absolute return from the premiums
        total_abs_return = ((row['CE_short_en_price'] - row['CE_short_ex_price']) +
                            (row['PE_short_en_price'] - row['PE_short_ex_price']) + 
                            (row['CE_long_ex_price'] - row['CE_long_en_price']) + 
                            (row['PE_long_ex_price'] - row['PE_long_en_price']))
        df.at[index, 'Abs_return'] = total_abs_return
        
        ## calculate straddle margin requirement
        ## (14% from total value(spot price * lot size) for each contracts + premium margin benefit)
        ## 60 % of the above value will yield us the margin requirement
        straddle_margin_req = ((2 * ((row['Fut_En_price'] * lot_size) / 14) +
                               row['CE_short_en_price'] * lot_size +
                               row['PE_short_en_price'] * lot_size) * 0.60)
        
        ## margin requirement for the wings
        wings_margin_req = row['CE_long_en_price'] * lot_size + row['PE_long_en_price'] * lot_size
        
        ## total margin requirement for one contracts of all the 4 
        total_margin_req = straddle_margin_req + wings_margin_req
        
        ## calculate the number of contracts to trade according to capital allocation percentage from the total capital
        if index == 1:
            prev_capital = capital
            
            num_contracts = math.floor((prev_capital * capital_allocation_per_trade) / total_margin_req)
        if index > 1:
            prev_capital = df.at[index - 1, 'Capital']
            
            num_contracts = math.floor((prev_capital * capital_allocation_per_trade) / total_margin_req)   
            
        df.at[index, 'Lot_size'] = lot_size
        df.at[index, 'Contracts'] = num_contracts
        
        ## PnL calculation
        pl = total_abs_return * num_contracts * lot_size
        df.at[index, 'P&L'] = pl
        
        ## calculate capital at end of the trade and return percent
        prev_capital = prev_capital + pl
        df.at[index, 'Capital'] = prev_capital
        df.at[index, 'Return_pct'] = (pl / (prev_capital - pl))*100