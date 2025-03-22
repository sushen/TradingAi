import shutil

# Path to the source file
source_file = r'C:\Users\user\PycharmProjects\TradingAiVersion9\small_crypto.db'

# Path to the destination folder
destination_folder = r'C:\Users\user\PycharmProjects\TradingAiVersionTen'

# Copy the file
shutil.copy(source_file, destination_folder)

print(f"File copied from {source_file} to {destination_folder}")
