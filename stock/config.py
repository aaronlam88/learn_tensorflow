db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'stock',
}

yahoo_finance_url = "https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_time}&period2={end_time}&interval=1d&events=history&includeAdjustedClose=true"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

create_table_query = """
    CREATE TABLE IF NOT EXISTS {symbol} (
        Date DATE PRIMARY KEY,
        Open FLOAT,
        High FLOAT,
        Low FLOAT,
        Close FLOAT,
        `Adj Close` FLOAT,
        Volume INT
    )
"""

insert_data_query = """
    INSERT IGNORE INTO {symbol} (Date, Open, High, Low, Close, `Adj Close`, Volume)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""