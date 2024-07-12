import pandas as pd
import numpy as np

def fip_model(df: pd.DataFrame, num_positions: int):
    """
    Takes in a dataframe of daily stock data and outputs a dataframe of symbols and weights representing a portfolio.
    """

    # Create additional columns
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    df['ret'] = df.groupby('symbol')['close'].pct_change()

    df['month'] = df['timestamp'].dt.to_period('M').astype(str)

    df['up'] = np.where(df['ret'] > 0, 1, 0)

    df['down'] = np.where(df['ret'] < 0, 1, 0)

    df['total'] = 1

###

    # Aggregate to monthly level
    df = df.groupby(['symbol','month'])[['timestamp','close','up','down', 'total']].agg({'timestamp': 'last','close': 'last','up':'sum','down':'sum', 'total':'sum'})

    df.reset_index("month",inplace=True)
    df.reset_index("symbol",inplace=True)

    # Create additional monthly columns
    df['%neg-%pos'] = (df['down']-df['up']) / df['total']

    df['ret'] = df.groupby('symbol')['close'].pct_change()

    df['logret'] = np.log(1 + df['ret'])

###    

    # Generate pret and id features
    df['pret'] = df.groupby('symbol')['logret'].rolling(11,11).sum().reset_index(drop=True)
    df['pret'] = df.groupby('symbol')['pret'].shift(2)

    df['id'] = df.groupby('symbol')['%neg-%pos'].rolling(11,11).mean().reset_index(drop=True)
    df['id'] = df.groupby('symbol')['id'].shift(2)

    df['id'] = np.sign(df['pret']) * df['id']

    df['mom_score'] = df['pret'] * abs(df['id'])

###

    print(df.head(25))

    # Filter universe by price and availability
    df['prclag'] = df.groupby('symbol')['close'].shift(1)

    df = df.query("pret == pret and id == id and prclag >= 5").reset_index(drop=True)



    # Bin universe on pret and id features
    df['mombins'] = df.groupby("timestamp")['pret'].transform(lambda x: pd.qcut(x, 2, labels=False))

    df['idbins'] = df.groupby('timestamp')['id'].transform(lambda x: pd.qcut(x, 5, labels=False))

    # Filter to best pret and id bins and sort by score
    df = df.query("mombins == 1 and idbins == 4")
    df = df.sort_values(by='mom_score', ascending=False)

###
    # Construct portfolio
    weight = 1 / num_positions

    df = df[['symbol']].iloc[0:num_positions]

    df = df.reset_index(drop=True)

    df['weight'] = weight

    return df



