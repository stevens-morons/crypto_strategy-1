import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import pyfolio as pf
import csv; import datetime; import pytz
from technical_indicators import BBANDS
from historical_data import exchange_data, write_to_csv, to_unix_time
# import backtest
import warnings
warnings.filterwarnings('ignore')

# ==========Initial trade parameters =============
symbol = 'BTC/USD'
timeframe = '1d'
since = '2017-01-01 00:00:00'
hist_start_date = int(to_unix_time(since))
header = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']

# ==========Initial exchange parameters =============
kraken = exchange_data('kraken','BTC/USD',timeframe=timeframe,since=hist_start_date)
write_to_csv(kraken,'BTC/USD','kraken')
data = pd.DataFrame(kraken,columns=header)

# =================================================================
# ================ DIRECTIONAL STRATEGY ===========================
stddev = 2

def strategy(data):
    '''
    :param data: dataframe with OHLCV
    :return: Strategy Returns and Equity Curve

    === Volatility Outburst Strategy ===
    Buy when Price closes above the Mean + default SD Value
    Sell when Price closes below the Mean - default SD Value

    '''

    data['returns'] = np.log(data['Close'].shift(1) / data['Close'])
    data['position'] = 0  # pd.Series(np.random.randn(len(data)), index=data.index)

    for period in range(10, 50, 5):
        bbands = BBANDS(data, stddev, period)

        for row in range(1, len(data)):
            if data['Close'].iloc[row] > bbands['BB_Upper'].iloc[row]:
                data['position'].iloc[row] = 1
            elif data['Close'].iloc[row] < bbands['BB_Lower'].iloc[row]:
                data['position'].iloc[row] = -1

            while data['position'].iloc[row - 1] == 1 and data['Close'].iloc[row] > bbands['BB_Lower'].iloc[row]:
                data['position'].iloc[row] = 1

            while (data['position'].iloc[row - 1] == -1) and (data['Close'].iloc[row] < bbands['BB_Upper'].iloc[row]):
                data['position'].iloc[row] = -1

    data['strat_returns'] = data['position'].shift(1) * data['returns']
    cum_returns = data['strat_returns'].dropna().cumsum().apply(np.exp)

    return data['strat_returns'], cum_returns

returns = strategy(data=data)
# backtest.drawdown_periods(returns)
# backtest.underwater_plot(returns)
