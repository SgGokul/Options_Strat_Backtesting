import pandas as pd
import math

## calculate sharpe ratio using the return percentage
def sharpe_ratio(df: pd.DataFrame) -> float:
    mean_pnl = (df['Return_pct']/100).mean()
    std_pnl = (df['Return_pct']/100).std()
    sr = math.sqrt(len(df)) * (mean_pnl/std_pnl)
    return sr

## calculate win rate/hit ratio
def win_rate(df: pd.DataFrame) -> float:
    wr = (len(df[df['Abs_return'] > 0])/len(df)) * 100
    return wr 

## calculate risk to reward ratio
def risk_reward(df: pd.DataFrame) -> float:
    rr = abs((df[df['Abs_return']<0]['Abs_return']).mean()) / (df[df['Abs_return']>0]['Abs_return']).mean() 
    return rr

## calculate calmar ratio
def calmar_ratio(df: pd.DataFrame) -> float:
    annualized_return = df['Cumulative_Returns'].iloc[-1] ** (252 / len(df)) - 1  
    max_drawdown = (df['Drawdown'].min())/100
    calmar_ratio = annualized_return / abs(max_drawdown)
    return calmar_ratio

## generate stats sheet as needed
def generate_stats_sheet(df: pd.DataFrame, capital: float) -> pd.DataFrame:
    total_trades = len(df)
    profitable_trades = df[df['P&L'] > 0]
    losing_trades = df[df['P&L'] < 0]
    hit_ratio = win_rate(df)
    sr = sharpe_ratio(df)
    cr = calmar_ratio(df)
    rr = risk_reward(df)
    
    avg_return_per_trade = df['Return_pct'].mean()
    avg_profit_per_trade = profitable_trades['Return_pct'].mean()
    avg_loss_per_trade = losing_trades['Return_pct'].mean()
    
    max_profit_per_trade = df['Return_pct'].max()
    max_loss_per_trade = df['Return_pct'].min()
    
    avg_return_per_month = df['Return_pct'].mean() * 21 
    avg_return_per_year = df['Return_pct'].mean() * 252 
    
    total_return = (df['Cumulative_Returns'].iloc[-1] - 1) * 100
    cagr_return = (((df['Capital'].iloc[-1] / capital)) - 1) * 100
    
    max_drawdown = df['Drawdown'].min()
    
    summary_dict = {
        'Stats': ['Capital', 'Total Trades', 'Profitable Trades', 'Losing Trades', 'Hit Ratio', 'Risk to Reward', 
                  'Avg Return Per Trade', 'Avg Profit Per Trade', 'Avg Loss Per Trade',
                  'Max Profit Per Trade', 'Max Loss Per Trade', 'Avg Return Per Month',
                  'Avg Return Per Year', 'Total Return', 'CAGR Return', 'Max Drawdown', 'Sharpe Ratio', 'Calmar Ratio'],
        'Percentage Return': [capital, total_trades, len(profitable_trades), len(losing_trades), f'{hit_ratio:.2f}%', f'{rr:.2f}%',
                              f'{avg_return_per_trade:.2f}%', f'{avg_profit_per_trade:.2f}%', f'{avg_loss_per_trade:.2f}%',
                              f'{max_profit_per_trade:.2f}%', f'{max_loss_per_trade:.2f}%', f'{avg_return_per_month:.2f}%',
                              f'{avg_return_per_year:.2f}%', f'{total_return:.2f}%', f'{cagr_return:.2f}%', f'{max_drawdown:.2f}%',
                              f'{sr:.2f}', f'{cr:.2f}'],
    }
    
    summary_df = pd.DataFrame(summary_dict)
    return summary_df

## calculate peak and drawdowns
def drawdown(df: pd.DataFrame) -> None:
    df['Cumulative_Returns'] = (1 + df['Return_pct'] / 100).cumprod()
    df['Peak'] = df['Cumulative_Returns'].cummax()
    df['Drawdown'] = ((df['Cumulative_Returns'] - df['Peak'] ) / df['Peak'])*100