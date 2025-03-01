import os
from binance.client import Client
from pprint import pprint

# Replace with your Binance API keys
API_KEY = os.environ.get('binance_api_key')
API_SECRET = os.environ.get('binance_api_secret')

# Initialize Binance Client
client = Client(API_KEY, API_SECRET)

try:
    # Fetch futures account balance
    # balance_info = client.futures_account_balance()

    balance_info = client.futures_account_balance()

    # Print the raw response for debugging
    print("Raw response from API:", balance_info)

    # Print the fetched balance in a more readable format
    pprint(balance_info)

except Exception as e:
    print(f"Error fetching futures balance: {e}")
