import matplotlib.pyplot as plt
import seaborn as sns

## plot equity and drawdown curve
def plot_equity_dd_curve(df):
    fig, ax1 = plt.subplots(figsize=(20, 13))

    sns.lineplot(data=df, x=df.index, y='Capital', color='blue', linewidth=3, label='Equity Curve', ax=ax1)
    ax1.set_ylabel('Capital')

    ax2 = ax1.twinx()

    sns.lineplot(data=df, x=df.index, y='Drawdown', color='red', linewidth=2, label='Drawdown Curve', ax=ax2)
    ax2.set_ylabel('Drawdown (%)')

    ax2.set_ylim(-25, 0)

    plt.title('Equity and Drawdown Curves')
    plt.xlabel('Date')
    plt.grid(True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower right')
    plt.show()