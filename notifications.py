from flask import render_template
import requests
import os

KEY = os.getenv('MAILGUN_API_KEY')
SANDBOX = os.getenv('MAILGUN_DOMAIN')
ENVIRONMENT = os.getenv('ENVIRONMENT')


def send_email(subject, body):
    if ENVIRONMENT == 'production':
        email = os.getenv('ADMIN_MAIL')
        recipient = os.getenv('NOTIFICATION_MAIL')

    elif ENVIRONMENT == 'staging':
        email = os.getenv('ADMIN_MAIL_STAGING')
        recipient = os.getenv('NOTIFICATION_MAIL_STAGING')

    else:
        print('***email***')
        print(body)
        return

    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(SANDBOX)
    request = requests.post(request_url, auth=('api', KEY), data={
        'from': email,
        'to': recipient,
        'subject': subject,
        'html': body
    })
    return request


def notify_new_order(address, user):
    body = render_template('new_order.html', address=address, user=user)
    send_email("Nuovo Ordine", body)


def notify_new_user(first_name, last_name):
    body = render_template('new_user.html', first_name=first_name, last_name=last_name)
    send_email("Nuovo Utente", body)
