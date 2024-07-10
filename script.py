import pandas as pd
import numpy as np
import pendulum
from dotenv import load_dotenv
import os

from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest 
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetStatus
from alpaca.trading.enums import AssetClass
from alpaca.data.enums import Adjustment
from alpaca.data.timeframe import TimeFrameUnit

# Environment Variables
load_dotenv()

api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_SECRET_KEY")


# Clients
data_client = StockHistoricalDataClient(api_key,secret_key)
trading_client = TradingClient(api_key,secret_key)

# Parameters
end = pendulum.datetime(2024,7,4)
start = end.subtract(days=2)

# Get all current assets
asset_request = GetAssetsRequest(
    # status = AssetStatus.ACTIVE,
    asset_class = AssetClass.US_EQUITY,
)

all_assets = trading_client.get_all_assets(asset_request)

all_assets = [vars(asset) for asset in all_assets] # Convert objects to dicts

df = pd.DataFrame(data=all_assets)

# df = df[df['tradable'] & df['fractionable'] & df['shortable']]

symbols = df['symbol'].to_list()

# Get previous days market data
bars_request = StockBarsRequest(
    symbol_or_symbols=symbols,
    timeframe=TimeFrame(1,TimeFrameUnit.Day),
    start=start,
    end=end,
    adjustment=Adjustment.ALL,
)

bars = data_client.get_stock_bars(bars_request)

df = bars.df

df = df.reset_index()

print(df)
