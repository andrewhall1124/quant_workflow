### First available day of data

    pendulum.datetime(2016,1,4,5,tz='UTC')

### Current Status
As of July 12th 2024 this airflow app pulls stock data from the alpaca API each day and loads it into a postgres database. Each month a similar dag runs to double check the data.

Also occuring monthly is a dag that compute frog in the pan portfolios that includes the top 100 stocks according to their momentum and information discreteness.
