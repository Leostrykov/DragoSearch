from tokens import generate_token
from flask import render_template
import smtplib
import mimetypes
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(email, subject, text, type_message):
    addr_from = os.getenv('MAIL_FROM')
    password = os.getenv('MAIL_PASSWORD')
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = email
    msg['Subject'] = subject

    body = text
    if type_message == 'text':
        msg.attach(MIMEText(body, 'plain'))
    elif type_message == 'html':
        msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL(os.getenv('MAIL_HOST'), os.getenv('MAIL_PORT'))
        server.login(addr_from, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f'Error send message {email}. Error: {e}')


def send_token(email):
    return send_email(email, 'Потвердите почту на DragoSearch',
                      render_template('confirm_message.html',
                                      confirm_url=f'https://'
                                                  f'soapy-spark-grass.glitch.me/confirm/{generate_token(email)}'),
                      'html')
