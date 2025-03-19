import requests
import os

from all_variable import Variable
# Set database path from Variable class
DISCORD_TOKEN = Variable.DISCORD_TOKEN
# print(DISCORD_TOKEN)

class Messages:
    def __init__(self):
        self.token = DISCORD_TOKEN
        self.channel_id = 1110038642786832444

    def send_massage(self, message):
        headers = {
            'Authorization': f'Bot {self.token}',
            'Content-Type': 'application/json'
        }

        url = f'https://discord.com/api/v9/channels/{self.channel_id}/messages'
        payload = {
            'content': message
        }

        response = requests.post(url, headers=headers, json=payload)

        # Debugging response details
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")

        response.raise_for_status()


if __name__ == "__main__":
    messages = Messages()
    messages.send_massage("Hello there!")

