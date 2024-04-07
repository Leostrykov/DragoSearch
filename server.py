from flask import Flask, render_template, request
from data import db_session
from data.users import User
from data.news import News
import os
from os.path import join, dirname
from dotenv import load_dotenv
from forms.login import LoginForm
from forms.sing_up import SingUpForm
import logging

# Загружаем ключи из .env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
file_handler = logging.FileHandler('errors.txt')
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != 1)
    return render_template('news.html', news=news)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form_login = LoginForm()
    form_sing_up = SingUpForm()
    if form_login.validate_on_submit() and form_login.submit_login.data:
        print(form_login.email.data)
        print(form_login.password.data)
        return 'Ok вошли'
    elif form_sing_up.validate_on_submit() and form_sing_up.submit_sing_up.data:
        print(form_sing_up.name.data)
        print(form_sing_up.email.data)
        print(form_sing_up.password.data)
        return 'Ok зарегались'
    return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up)


@app.route('/sing-up', methods=['POST', 'GET'])
def sing_up_mobile():
    form_sing_up = SingUpForm()
    if form_sing_up.validate_on_submit() and form_sing_up.submit_sing_up.data:
        return 'Ok тел зареган'
    return render_template('sing-up-for-mobile.html', form_sing_up=form_sing_up)


if __name__ == '__main__':
    db_session.global_init('.data/news.db')
    app.run()
