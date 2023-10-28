
import requests
import random
import os
from twilio.rest import Client
from django.conf import settings



# TWILIO_AUTH_TOKEN = '2198174812d64a4d9e191bbcb649e7e1'
# TWILIO_ACCOUNT_SID = 'AC41b12c18ef997d6aece1818205af087d'
# otp = random.randint(100000,999999)
# def send_otp_phone(otp):
#     account_sid = TWILIO_ACCOUNT_SID
#     auth_token = TWILIO_AUTH_TOKEN
#     client = Client(account_sid, auth_token)

#     message = client.messages \
#         .create(
#             from_='+12569371129',
#             body=f"Your one time password is {otp}",
#             to='+918075026919'
#         )

#     print(message.body)


def send_otp_phone(otp,phonenumber):
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {"authorization":"wXSvDPxq8NdcRjoYZsUkgaz2V5TCJHrOhLM4Blt97uyif3A16QhXaWLxO5K8uCRStyY7Jgd1rsFmvIji","variables_values":otp,"route":"otp","numbers":phonenumber}

    headers = {
    'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
