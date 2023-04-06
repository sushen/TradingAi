import os
import time
from binance.client import Client

api_key = os.environ.get('binance_api_key')
api_secret = os.environ.get('binance_api_secret')

client = Client(api_key, api_secret)
server_time = client.get_server_time()

# Get the current system time
system_time = int(time.time() * 1000)

# Calculate the time difference between the server time and system time
time_diff = server_time - system_time

# Print the time difference
print(f"System time is off by {time_diff} milliseconds from server time")

# If the time difference is more than 1 second, warn the user
if abs(time_diff) > 1000:
    print("Warning: System clock is significantly out of sync with server clock!")
