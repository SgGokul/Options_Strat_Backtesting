backtester.py is the primary python file that needs to be run,
by calling different functions from different python files it will generate 
the tradelog, equity-drawdown curve and the stats sheet

data_processing.py and bnd_ohlcv_data.py ---> these are files used for data cleaning and processing

backtesting_class.py ---> it contains the class to backtest the strategy, that generates the initial tradelog

pnl_generator.py ---> it is to generate pnl and calculate capital throughout the period

trade_analysis.py and plot.py ---> it is used for the calculation of the stats that are needed and to plot graphs