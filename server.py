from flask import Flask, render_template
from data import db_session
from data.users import User
from data.news import News
import os
from os.path import join, dirname
from dotenv import load_dotenv
from forms.login import LoginForm
from forms.sing_up import SingUpForm
import logging

# Закружаем ключи из .env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
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
    if form_login.validate_on_submit():
        print(form_login.email.data)
        print(form_login.password.data)
        return 'Ok'
    elif form_sing_up.validate_on_submit():
        print(form_sing_up.name.data)
        print(form_sing_up.email.data)
        print(form_sing_up.password.data)
        return 'Ok'
    return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up)


@app.route('/sing-up', methods=['POST', 'GET'])
def sing_up_mobile():
    return render_template('sing-up-for-mobile.html')


def craete_news():
    db_sess = db_session.create_session()
    news = News(title="Первая моя новость", content="Я так рад что это моя первый пост!!!!!",
            user_id=2, is_private=False)
    db_sess.add(news)
    db_sess.commit()


if __name__ == '__main__':
    db_session.global_init('db/news.db')
    app.run()
