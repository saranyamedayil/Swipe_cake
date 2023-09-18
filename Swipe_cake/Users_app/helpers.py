
import requests
import random
import os
from twilio.rest import Client
from django.conf import settings


TWILIO_AUTH_TOKEN = '9a7ea01e148e484042aa3644cf686a9e'
TWILIO_ACCOUNT_SID = 'AC41b12c18ef997d6aece1818205af087d'
otp = random.randint(100000,999999)
def send_otp_phone(otp):
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            from_='+12569371129',
            body=f"Your one time password is {otp}",
            to='+918075026919'
        )

    print(message.body)
