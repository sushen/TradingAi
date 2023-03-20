import os
import time

from binance.client import Client

# from email_option.sending_mail import MailSender
# from all_variable import Variable

# gmail = Variable.MAIL
# receiver_mail = gmail
# message = f'Check you heruku for get exception .'

api_key = os.environ.get('binance_api_key')
api_secret = os.environ.get('binance_api_secret')
client = Client(api_key, api_secret)
print(client.get_ticker())

class APICall:
    try:
        api_key = os.environ.get('binance_api_key')
        api_secret = os.environ.get('binance_api_secret')
        client = Client(api_key, api_secret)
    except:
        # sender1 = MailSender()
        # sender1.login()

        email_subject = "Api have and exception"
        email_body = "See heroku logs its give you an idea what is the error?"

        # sender1.send_mail(gmail, email_subject, email_body)
        print(f'{email_subject}\n\n {email_body}')

        print(input("----"))
        time.sleep(61)
        api_key = os.environ.get('binance_api_key')
        api_secret = os.environ.get('binance_api_secret')
        client = Client(api_key, api_secret)


APICall.client.get_ticker()