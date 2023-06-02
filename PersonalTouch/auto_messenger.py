from fbchat import Client
from fbchat.models import *
import os


class Messenger:

    def __init__(self):
        self.id = os.environ.get('facebook_email')
        self.password = os.environ.get('facebook_pass')
        self.client = Client(self.id, self.password)

    def find_unread_messages(self):
        # Fetch the list of unread messages
        unread_messages = self.client.fetchUnread()

        # Print the unread messages
        thread_ids = []
        for uid in unread_messages:
            try:
                user = self.client.fetchThreadInfo(uid)[str(uid)]
                if user.type == ThreadType.USER:
                    print(f"Unread message from {uid}")
                    thread_ids.append(uid)
            except Exception as e:
                print(e)
        return thread_ids

    def send_message(self, user_id, message_text):
        try:
            # Send the message
            self.client.send(Message(text=message_text), thread_id=user_id, thread_type=ThreadType.USER)
            print("Message sent successfully!")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    messenger = Messenger()
    user_ids = messenger.find_unread_messages()
    messenger.send_message(user_ids[0], "Hello")
