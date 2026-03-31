import yfinance as yf
import pandas as pd
import os

print(" Downloading fresh AAPL data...")
df = yf.download("AAPL", period="1mo", interval="1h", progress=False)

# Clean up the data
df = df.reset_index()
df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']

# Convert datetime to string
df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save to CSV (create directory if needed)
os.makedirs("server/data", exist_ok=True)
df.to_csv("server/data/prices.csv", index=False)
print(f"Saved {len(df)} rows of clean data")
print("\nFirst 3 rows:")
print(df[['datetime', 'close']].head(3))
print("\nLast 3 rows:")
print(df[['datetime', 'close']].tail(3))
