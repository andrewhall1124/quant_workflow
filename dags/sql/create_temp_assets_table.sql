DROP TABLE IF EXISTS TEMP_ASSETS;
CREATE TABLE IF NOT EXISTS TEMP_ASSETS (
    ID TEXT PRIMARY KEY,
    ASSET_CLASS TEXT,
    EXCHANGE TEXT,
    SYMBOL TEXT,
    NAME TEXT,
    STATUS TEXT,
    TRADABLE BOOLEAN,
    MARGINABLE BOOLEAN,
    SHORTABLE BOOLEAN,
    EASY_TO_BORROW BOOLEAN,
    FRACTIONABLE BOOLEAN,
    MIN_ORDER_SIZE NUMERIC,
    MIN_TRADE_INCREMENT NUMERIC,
    PRICE_INCREMENT NUMERIC,
    MAINTENANCE_MARGIN_REQUREMENT NUMERIC,
    ATTRIBUTES TEXT,
    INSERT_ID TEXT,
    UPDATE_ID TEXT
);