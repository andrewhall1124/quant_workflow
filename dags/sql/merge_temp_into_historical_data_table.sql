INSERT INTO HISTORICAL_DATA (
    SYMBOL,
    TIMESTAMP,
    OPEN,
    HIGH,
    LOW,
    CLOSE,
    VOLUME,
    TRADE_COUNT,
    VWAP
)
SELECT
    SYMBOL,
    TIMESTAMP,
    OPEN,
    HIGH,
    LOW,
    CLOSE,
    VOLUME,
    TRADE_COUNT,
    VWAP
FROM TEMP_HISTORICAL_DATA
ON CONFLICT (SYMBOL, TIMESTAMP) DO UPDATE
SET
    OPEN = EXCLUDED.OPEN,
    HIGH = EXCLUDED.HIGH,
    LOW = EXCLUDED.LOW,
    CLOSE = EXCLUDED.CLOSE,
    VOLUME = EXCLUDED.VOLUME,
    TRADE_COUNT = EXCLUDED.TRADE_COUNT,
    VWAP = EXCLUDED.VWAP;