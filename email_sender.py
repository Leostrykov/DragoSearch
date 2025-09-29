from tokens import generate_token
from flask import render_template
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv('MAIL_HOST')
SMTP_PORT = os.getenv('MAIL_PORT')
SMTP_LOGIN = os.getenv('MAIL_LOGIN')
SMTP_PASS = os.getenv('MAIL_PASSWORD')
SMTP_FROM = os.getenv('MAIL_FROM')


# функция отправления сообщения
def send_email(email, subject, text, type_message):
    msg = MIMEMultipart()
    msg['From'] = SMTP_FROM
    msg['To'] = email
    msg['Subject'] = subject

    body = text
    if type_message == 'text':
        msg.attach(MIMEText(body, 'plain'))
    elif type_message == 'html':
        msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT))
        server.login(SMTP_LOGIN, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f'Error send message {email}. Error: {e}')


# функция отправки подтверждения
def send_token(email):
    return send_email(email, 'Подведите почту на DragoSearch',
                      render_template('confirm_message.html',
                                      confirm_url=os.getenv('BASE_URL') + 'confirm/' + generate_token(email)),'html')