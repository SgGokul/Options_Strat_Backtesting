# Options_Strat_Backtesting

1.	Sell an ATM straddle at 10:30 am by simultaneously selling both an ATM call option and an ATM put option with the same WEEKLY expiry date and strike price. 
2.	Buy 2% away wings for protection by buying both an out-of-the-money call option and an out-of-the-money put option with strike prices 2% higher and lower than the ATM strike, respectively.
3.	Calculate the 30% stop loss based on the premium collected from selling the straddle.
4.	Monitor the position for the rest of the trading days and exit all legs of the trade together if either of the following conditions is met:
o	The 30% stop loss is hit.
o	The target of 80% is achieved.
5.	If neither condition is met, hold the position until the expiry time of 3:20 pm and exit all legs of the trade together.

   Backtesting Period : Year 2017 ; Instrument : BANKNIFTY Futures & Options
   Link to Data : https://drive.google.com/drive/folders/1c4iiWbfzmPPoMWk08jUeqz0YL_yheM8Y?usp=sharing
   

![equity_dd_curve](https://github.com/SgGokul/Options_Strat_Backtesting/assets/107173414/0c570ce5-487e-4169-91c4-372b7f40afb9)

<img width="196" alt="image" src="https://github.com/SgGokul/Options_Strat_Backtesting/assets/107173414/8cce3252-f412-4eaf-8747-82a5efcdedcd">

