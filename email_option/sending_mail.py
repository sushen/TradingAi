"""
This class base on this article :
https://medium.com/@manavshrivastava/how-to-send-emails-using-python-c89b802e0b05

1. you have to change the receiver email to get the email to your inbox
2. Create a environment variable "GMAIL"to your system to set your email
3. Use Google app password to generate password :
    https://myaccount.google.com/apppasswords

"""
import smtplib
import os

gmail = os.environ.get('GMAIL')
gmail_password = os.environ.get('GMAIL_PASSWORD')


class MailSender:

    smtp_server = "smtp.gmail.com"
    ssl_port = 465
    sender_mail = gmail
    user_mail = gmail
    password = gmail_password

    def login(self):
        server = smtplib.SMTP_SSL(self.smtp_server, self.ssl_port)
        server.ehlo()
        server.login(self.user_mail, self.password)
        return server

    def send_mail(self, receiver_mail, SUBJECT, TEXT):
        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        server = self.login()
        server.sendmail(self.sender_mail, receiver_mail, message)
        server.close()


if __name__ == "__main__":
    sender1 = MailSender()
    print('Server creation is completed', )

    sender1.login()
    print(f"We send email_option from : {gmail}")
    print('Login Success')

    test_subject = "Mango People"
    test_Body = "Normal civilian means Mango People  ,in Bangla its means AmJanata"

    sender1.send_mail("zihad.bscincse@gmail.com", test_subject, test_Body)
    print('Email Sent')