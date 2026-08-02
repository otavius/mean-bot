from datetime import datetime 

import MetaTrader5 as mt5
import pandas as pd 
import pytz

if not mt5.initialize():
    raise RuntimeError(f"Failed to initialize mt5. Error: {mt5.last_error()}")


"""
Global variables
"""
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1


def zscore(symbol: str, timeframe = mt5.TIMEFRAME_H1, window: int = 20, date_from=None, date_to=None):
    timezone = pytz.timezone("US/Eastern")
    date_from = datetime(2026, 1, 1, tzinfo=timezone)
    date_to = datetime(2026, 8, 2, tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol,timeframe,date_from, date_to)
    if rates is None or len(rates) < window: 
        return 

    rates_df = pd.DataFrame(data=rates).copy()
    rates_df["rolling_mean"]= rates_df["close"].rolling(window=window).mean() 
    rates_df["rolling_std"] = rates_df["close"].rolling(window=window).std()
    rates_df["zscore"] = (rates_df["close"] - rates_df["rolling_mean"]) / rates_df["rolling_std"]


    return rates_df.dropna()



if __name__ == "__main__":
    print(zscore("GBPJPY", mt5.TIMEFRAME_H1, window=20))
    mt5.shutdown()