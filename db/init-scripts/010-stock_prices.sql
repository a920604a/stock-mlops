CREATE TABLE public.stock_prices (
    "Date" timestamptz NULL,
    "Open" float8 NULL,
    "High" float8 NULL,
    "Low" float8 NULL,
    "Close" float8 NULL,
    "Volume" int8 NULL,
    "Dividends" float8 NULL,
    "Stock Splits" float8 NULL,
    "MA10" float8 NULL,
    ticker text NULL,
    exchange text NULL
);