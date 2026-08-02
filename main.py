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
    print(rates_df.columns)


    return rates_df.dropna()

def backtest(df, entry_z: float = 2.0, exit_z: float = 0.5, stop_z: float = 3.5):
    position = 0 # 0 = flat, 1 = long, 2 = short
    entry_price = None
    trades = []

    for i in range(len(df) -1):
        current = df.iloc[i]
        next_bar = df.iloc[i + 1]
        if position == 0:
            if current["zscore"] > entry_z:
                position = 2
                entry_price = next_bar["open"]
            elif current["zscore"] < -entry_z:
                position = 1
                entry_price = next_bar["open"]
        elif position != 0:
            if abs(current["zscore"]) >= stop_z:
                # close position at loss
                if position == 1: 
                    exit_price = next_bar["open"]
                    pnl = exit_price - entry_price
                elif position == 2:
                    exit_price = next_bar["open"]
                    pnl = entry_price - exit_price


                trades.append(dict({
                    "entry_price": entry_price,
                    "exit_price":exit_price, 
                    "pnl": pnl,
                    "position": position,
                    "reason": "stop out"
                }))
                position = 0
                entry_price = None
            elif abs(current["zscore"]) < exit_z:
                if position == 1: 
                    exit_price = next_bar["open"]
                    pnl = exit_price - entry_price
                elif position == 2:
                    exit_price = next_bar["open"]
                    pnl = entry_price -  exit_price


                trades.append(dict({
                    "entry_price": entry_price,
                    "exit_price":exit_price, 
                    "pnl": pnl,
                    "position": position,
                    "reason": "exit trade"
                }))
                position = 0 
                entry_price = None

    return trades

if __name__ == "__main__":
    #print(zscore("GBPJPY", mt5.TIMEFRAME_H1, window=20))
    data = zscore("EURUSD", mt5.TIMEFRAME_H1, window=20)
    trades = backtest(data)
    reasons = [t["reason"] for t in trades]
    print(f"stop out = {reasons.count("stop out")}, exits = {reasons.count("exit trade")}")
    print(len(trades))
    print(trades[:5])

    mt5.shutdown()