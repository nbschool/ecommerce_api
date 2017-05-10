import requests
import os

KEY = os.getenv('MAILGUN_API_KEY')
SANDBOX = os.getenv('MAILGUN_DOMAIN')
ENVIRONMENT = os.getenv('ENVIRONMENT')


def send_email(subject, body):

    if ENVIRONMENT == 'dev':
        print('Status: 200')
        print('Body: Trying send email')
        return

    elif ENVIRONMENT == 'staging':
        email = os.getenv('ADMIN_MAIL_STAGING')
        recipient = os.getenv('NOTIFICATION_MAIL_STAGING')

    else:
        email = os.getenv('ADMIN_MAIL')
        recipient = os.getenv('NOTIFICATION_MAIL')

    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(SANDBOX)
    request = requests.post(request_url, auth=('api', KEY), data={
        'from': email,
        'to': recipient,
        'subject': subject,
        'html': body
    })
    return request
