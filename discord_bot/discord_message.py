import requests


class Messages:
    def __init__(self):
        self.token = 'MTExMDA0MTc4NDA3NzI2Mjg0OA.GrDsoe.4YmxI7vul5L_lRFprr5GSD1dMXHyRiVd_kXuh0'
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
        response.raise_for_status()


if __name__ == "__main__":
    messages = Messages()
    messages.send_massage("Hello their!")