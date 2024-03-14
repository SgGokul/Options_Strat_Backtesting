from backtesting_class import backtesting
from pnl_generator import calculate_margin_and_capital
from trade_analysis import drawdown, generate_stats_sheet
from plot import plot_equity_dd_curve

## path to csv files
filepath_fut = 'Data/fut.csv'
filepath_opt = 'Data/options.csv'

## params
capital = 1000000
wing_percent = 0.02
sl = 0.3
tp = 0.8

## assumptions :  80% of the total capital is used to trade and the lot size of a contract is 15
capital_allocation_per_trade = 0.80
lot_size = 15

## backtest the strategy and extract the tradebook
Model = backtesting(filepath_fut, filepath_opt, capital, wing_percent, sl, tp)
df = Model.test_strat()

## calculate returns, capital growth, PnL
calculate_margin_and_capital(df, lot_size, capital, capital_allocation_per_trade)
## calculate drawdown
drawdown(df)
## extract the stats for the strategy
stats = generate_stats_sheet(df, capital)
print(stats)
plot_equity_dd_curve(df)

print(df)