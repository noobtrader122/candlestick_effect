import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

# Fetch BTC/USD historical data
def fetch_data(ticker="BTC-USD", interval="5m", start_date="2020-01-01"):
    data = yf.download(ticker, interval=interval, period='1mo')
    data["Return"] = data["Close"].pct_change()
    print(data)
    return data

# Identify candlestick patterns
def identify_patterns(data):
    # Bullish Engulfing
    data["Bullish_Engulfing"] = (
        (data["Open"].shift(1) > data["Close"].shift(1)) & 
        (data["Open"] < data["Close"]) & 
        (data["Open"] < data["Close"].shift(1)) & 
        (data["Close"] > data["Open"].shift(1))
    )

    # Bearish Engulfing
    data["Bearish_Engulfing"] = (
        (data["Open"].shift(1) < data["Close"].shift(1)) & 
        (data["Open"] > data["Close"]) & 
        (data["Open"] > data["Close"].shift(1)) & 
        (data["Close"] < data["Open"].shift(1))
    )

    # Doji (small body)
    data["Doji"] = (
        (abs(data["Close"] - data["Open"]) <= 0.001 * data["Close"]) & 
        ((data["High"] - data["Low"]) > 2 * abs(data["Close"] - data["Open"]))
    )

    # Bullish Reversal (Hammer-like pattern)
    data["Bullish_Reversal"] = (
        (data["Close"] > data["Open"]) &  
        ((data["Low"] < data["Open"]) & ((data["High"] - data["Close"]) <= 0.5 * (data["Close"] - data["Open"])))
    )

    # Bearish Reversal (Shooting Star-like pattern)
    data["Bearish_Reversal"] = (
        (data["Open"] > data["Close"]) &  
        ((data["High"] > data["Open"]) & ((data["Low"] - data["Close"]) <= 0.5 * (data["Open"] - data["Close"])))
    )
    return data

# Assess success (e.g., price increase/decrease within n days)
def evaluate_success(data, lookahead=5, threshold=0.05):
    results = {}
    patterns = ["Bullish_Engulfing", "Bearish_Engulfing", "Doji", "Bullish_Reversal", "Bearish_Reversal"]
    for pattern in patterns:
        results[pattern] = []
        for i in data.index:
            if data.loc[i, pattern].item():
                future = data.loc[i:i + pd.Timedelta(days=lookahead)]
                if "Bullish" in pattern:
                    success = (future["Close"].max() - data.loc[i, "Close"]) / data.loc[i, "Close"] >= threshold
                elif "Bearish" in pattern:
                    success = (data.loc[i, "Close"] - future["Close"].min()) / data.loc[i, "Close"] >= threshold
                else:
                    success = False  # Doji: Define its success criteria if needed
                results[pattern].append(success)
            else:
                results[pattern].append(False)
        data[f"{pattern}_Success"] = results[pattern]
    return data

# Visualization
def visualize(data):
    plt.figure(figsize=(14, 7))
    patterns = ["Bullish_Engulfing", "Bearish_Engulfing", "Doji", "Bullish_Reversal", "Bearish_Reversal"]
    colors = ["green", "red", "blue", "orange", "purple"]
    
    plt.plot(data.index, data["Close"], label="BTC-USD Price", color="black")
    for pattern, color in zip(patterns, colors):
        plt.scatter(
            data[data[pattern]].index,
            data[data[pattern]]["Close"],
            color=color, label=f"{pattern.replace('_', ' ')}", alpha=0.7
        )
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("BTC-USD Price with Candlestick Patterns")
    plt.legend()
    plt.show()

# Main Function
if __name__ == "__main__":
    patterns = ["Bullish_Engulfing", "Bearish_Engulfing", "Doji", "Bullish_Reversal", "Bearish_Reversal"]
    data = fetch_data()
    data = identify_patterns(data)
    data = evaluate_success(data)
    
    # Print success rates
    for pattern in patterns:
        print(f"Success Rate for {pattern.replace('_', ' ')}: {data[f'{pattern}_Success'].mean() * 100:.2f}%")
    
    visualize(data)
