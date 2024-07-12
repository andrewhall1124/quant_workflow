import pandas as pd
import numpy as np
from db import DB

db = DB()

def fip_model(daily: pd.DataFrame):
    """
    Takes in a dataframe of daily stock data and outputs a dataframe of symbols and weights representing a portfolio.
    """
    daily['mdt'] = daily['caldt'].dt.to_period('M').astype(str)

    daily['up'] = np.where(daily['ret'] > 0, 1, 0)

    daily['down'] = np.where(daily['ret'] < 0, 1, 0)

    daily['total'] = 1

    daily = daily.groupby(['permno','mdt'])[['caldt','prc','up','down', 'total']].agg({'caldt': 'last','prc': 'last','up':'sum','down':'sum', 'total':'sum'})

    daily.reset_index("mdt",inplace=True)
    daily.reset_index("permno",inplace=True)

    daily['%neg-%pos'] = (daily['down']-daily['up']) / daily['total']

    daily = daily[['permno','caldt','%neg-%pos']]

    monthly = monthly[['permno','caldt','prc','ret', 'shr']]



