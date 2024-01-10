# symbol_retrieval.py
import re
import time
from mysql.connector import connect, Error
from config import db_config, yahoo_finance_url, headers, create_table_query, insert_data_query
import pandas as pd
from io import StringIO
import requests
import argparse
from datetime import datetime, timedelta

class SymbolRetrieval:
    def __init__(self, db_config, yahoo_finance_url, create_table_query, insert_data_query, verbose=False):
        self.db_config = db_config
        self.yahoo_finance_url = yahoo_finance_url
        self.create_table_query = create_table_query
        self.insert_data_query = insert_data_query
        self.verbose = verbose

    def get_symbols_from_database(self):
        try:
            with connect(**self.db_config) as connection:
                cursor = connection.cursor(dictionary=True)

                # Execute the query to select all symbols from the 'symbol' table
                cursor.execute("SELECT symbol FROM symbol")

                # Fetch all the symbols
                symbols = [row['symbol'] for row in cursor.fetchall()]

                return symbols

        except Error as e:
            print(f"Error: {e}")
            return None

    def create_table_if_not_exists(self, symbol, connection):
        try:
            cursor = connection.cursor()

            # Remove non-alphabetical characters from the symbol for the table name
            table_name = re.sub(r'[^a-zA-Z]', '', symbol)

            # Execute a query to create the table if it doesn't exist
            cursor.execute(self.create_table_query.format(symbol=table_name))

            connection.commit()
        except Error as e:
            print(f"Error creating table for {symbol}: {e}")

    def insert_data_into_table(self, symbol, data, connection):
        try:
            cursor = connection.cursor()

            symbol =re.sub(r'[^a-zA-Z]', '', symbol)
            # Insert data into the corresponding table
            for index, row in data.iterrows():
                cursor.execute(self.insert_data_query.format(symbol=symbol),
                               (row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume']))

            connection.commit()
        except Error as e:
            print(f"Error inserting data into {symbol} table: {e}")
        
    def download_stock_data(self, symbol, start_time, end_time, max_retries=3, retry_delay=2):
        url = self.yahoo_finance_url.format(symbol=symbol, start_time=start_time, end_time=end_time)

        for attempt in range(1, max_retries + 1):
            response = requests.get(url, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Explicitly set the 'Date' column during DataFrame creation
                data = pd.read_csv(StringIO(response.text), parse_dates=['Date'])

                # Drop rows with missing values
                data = data.dropna()

                required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

                # Ensure that the required columns are present
                if set(required_columns).issubset(data.columns):
                    data['Symbol'] = re.sub(r'[^a-zA-Z]', '', symbol)  # Add a column for the symbol
                    return data
                else:
                    raise ValueError("Missing required columns in the downloaded data.")
            elif response.status_code == 404:
                if self.verbose:
                    print(f"Symbol {symbol} not found. Removing from the symbol table.")

                # Remove the symbol from the symbol table
                self.remove_symbol_from_table(symbol)
                return None  # Return None to indicate that the symbol was not found
            else:
                if self.verbose:
                    print(f"Failed to fetch data. Attempt {attempt}/{max_retries}. HTTP Status Code: {response.status_code}")

                # Wait for the specified delay before retrying
                time.sleep(retry_delay)

        raise ValueError(f"Max retries reached. Unable to fetch data from {url}")

    
    def remove_symbol_from_table(self, symbol):
        try:
            with connect(**self.db_config) as connection:
                cursor = connection.cursor()

                # Execute the query to remove the symbol from the 'symbol' table
                cursor.execute("DELETE FROM symbol WHERE symbol = %s", (symbol,))

                connection.commit()
        except Error as e:
            print(f"Error removing symbol {symbol} from the symbol table: {e}")
    
    def get_latest_date_from_table(self, symbol, connection):
        try:
            cursor = connection.cursor(dictionary=True)

            # Execute the query to select the latest date from the table
            cursor.execute(f"SELECT MAX(Date) as latest_date FROM {symbol}")
            result = cursor.fetchone()

            if result and result['latest_date']:
                return result['latest_date'].strftime('%Y-%m-%d')
            else:
                # If the table is empty, return None or a default value as needed
                return None
        except Error as e:
            print(f"Error: {e}")
            return None

    def main(self):
        # Get symbols from the database
        symbols_from_database = self.get_symbols_from_database()

        try:
            with connect(**self.db_config) as connection:
                # Download and insert data for each symbol
                for symbol in symbols_from_database:
                    # Get the latest date from the table
                    latest_date = self.get_latest_date_from_table(symbol, connection)

                    # Use the latest date as the start_time
                    start_time = latest_date if latest_date else (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                    
                    # Set end_time to today
                    end_time = datetime.now().strftime('%Y-%m-%d')

                    # Convert start_time and end_time to timestamps
                    start_timestamp = int(datetime.strptime(start_time, '%Y-%m-%d').timestamp())
                    end_timestamp = int(datetime.strptime(end_time, '%Y-%m-%d').timestamp())

                    # Download and insert data for the symbol
                    stock_data = self.download_stock_data(symbol, start_timestamp, end_timestamp)

                    # Check if stock_data is not None before proceeding
                    if stock_data is not None:
                        if self.verbose:
                            print(f"Data for {symbol} between {start_time} and {end_time}:")
                            print(stock_data)

                        # Create table if it doesn't exist
                        self.create_table_if_not_exists(symbol, connection)

                        # Insert data into the corresponding table
                        self.insert_data_into_table(symbol, stock_data, connection)

        except Error as e:
            print(f"Error connecting to the database: {e}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Download stock data for symbols from a MySQL database.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")
    args = parser.parse_args()

    # Create an instance of the SymbolRetrieval class with the config from config.py
    symbol_retrieval = SymbolRetrieval(db_config, yahoo_finance_url, create_table_query, insert_data_query, verbose=args.verbose)

    # Call the main method with command-line arguments
    symbol_retrieval.main()
