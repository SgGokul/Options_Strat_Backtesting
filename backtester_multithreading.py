import concurrent.futures
import pandas as pd
import time
from datetime import datetime, timedelta
from backtesting_class import backtesting
from pnl_generator import calculate_margin_and_capital
from trade_analysis import drawdown, generate_stats_sheet
from typing import List, TypeVar, Dict


## function to run backtesting for a given entry time
def run_backtest(entry_time: str, filepath_fut: str, filepath_opt: str, capital: float, wing_percent: float, sl: float, tp: float, capital_allocation_per_trade: float, lot_size: int) -> Dict[str, pd.DataFrame]:
    ## backtest the strategy and extract the tradebook
    Model = backtesting(filepath_fut, filepath_opt, capital, wing_percent, sl, tp)
    df = Model.test_strat(entry_time)
    ## calculate returns, capital growth, PnL
    calculate_margin_and_capital(df, lot_size, capital, capital_allocation_per_trade)
    ## calculate drawdown
    drawdown(df)
    ## extract the stats for the strategy
    stats = generate_stats_sheet(df, capital)
    
    return stats
    

## define parameters
filepath_fut = 'Data/fut.csv'
filepath_opt = 'Data/options.csv'
capital = 1000000
wing_percent = 0.02
sl = 0.3
tp = 0.8
capital_allocation_per_trade = 0.80
lot_size = 15

## generate entry times
start_time = "10:00"
end_time = "11:30"
delta = timedelta(minutes=1)
entry_times = [(datetime.strptime(start_time, "%H:%M") + i * delta).strftime("%H:%M") for i in range(int((datetime.strptime(end_time, "%H:%M") - datetime.strptime(start_time, "%H:%M")).total_seconds() / 60))]

## split entry_times into chunks
chunk_size = 10
entry_time_chunks = [entry_times[i:i + chunk_size] for i in range(0, len(entry_times), chunk_size)]

## dictionary to store results
results: Dict[str, pd.DataFrame] = {}

## function to run backtests in multithreading way for each chunk of entry times
def run_backtests(entry_time_chunk: List[str], filepath_fut: str, filepath_opt: str, capital: float, wing_percent: float, sl: float, tp: float, capital_allocation_per_trade: float, lot_size: int) -> None:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(run_backtest, entry_time, filepath_fut, filepath_opt, capital, wing_percent, sl, tp, capital_allocation_per_trade, lot_size): entry_time for entry_time in entry_time_chunk}
        for future in concurrent.futures.as_completed(futures):
            entry_time = futures[future]
            try:
                result = future.result()
                results[entry_time] = result
            except Exception as exc:
                print(f"Entry time {entry_time} generated an exception: {exc}")

starting_time = time.time()

i=1
## run backtests for each chunk of entry times
for chunk in entry_time_chunks:
    print(f"chunk {i} in progress, for entry time values : {chunk}")
    run_backtests(chunk, filepath_fut, filepath_opt, capital, wing_percent, sl, tp, capital_allocation_per_trade, lot_size)
    print(f"Done with backtesting of chunk {i}")
    i+=1


print(results)

ending_time = time.time() - starting_time

print("Total time taken to run the backtest: ", ending_time)