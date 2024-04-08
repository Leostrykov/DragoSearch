from flask import Flask, render_template, request, redirect, jsonify
from requests import post, get
from data import db_session
from data.users import User
from data.news import News
import os
from os.path import join, dirname
from dotenv import load_dotenv
from forms.login import LoginForm
from forms.sing_up import SingUpForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from email_sender import send_token, send_email
from tokens import confirm_token
import datetime
from urllib.parse import urlencode

# Загружаем ключи из .env, т.к glitch скрывает эти ключи от пользователей
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT')
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# главная страница
@app.route('/')
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != 1)
    return render_template('news.html', title='DragoSearch', news=news)


# страница входа
@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form_login = LoginForm()
    form_sing_up = SingUpForm()
    if form_login.validate_on_submit() and form_login.submit_login.data:
        try:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form_login.email.data).first()
            if user and user.check_password(form_login.password.data):
                login_user(user, remember=True)
                send_email(user.email, 'Новый вход на DragoSearch',
                           f'Вы вошли в DragoSearch '
                           f'в {datetime.datetime.now().strftime("%A %d-%B-%y %H:%M:%S")} '
                           f'\n---\nС уважением отдел оповещений DragoSearch', 'text')
                return redirect('/')
            return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                   message_login='Неверный пароль или почта')
        except Exception as e:
            print(f'Error login. Error: {e}')

    elif form_sing_up.validate_on_submit() and form_sing_up.submit_sing_up.data:
        try:
            db_sess = db_session.create_session()
            is_not_log = db_sess.query(User).filter(User.email == form_sing_up.email.data).first()
            if is_not_log is not None:
                return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                       message_sing_up='Пользователь с такой почтой уже существует')
            user = User(name=form_sing_up.name.data, email=form_sing_up.email.data)
            user.set_password(form_sing_up.password.data)
            db_sess.add(user)
            db_sess.commit()
            login_user(user, remember=True)
            if send_token(form_sing_up.email.data):
                return render_template('confirm_email.html', email=form_sing_up.email.data)
            else:
                return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                       message_sing_up='Не удалось отправить сообщение с подверждением.')

        except Exception as e:
            print(f'Error sing_up email:{form_sing_up.email.data}. Error:{e}')

    return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up)


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


# страница регистрации для мобильников
@app.route('/sing-up', methods=['POST', 'GET'])
def sing_up_mobile():
    form_sing_up = SingUpForm()
    if form_sing_up.validate_on_submit() and form_sing_up.submit_sing_up.data:
        try:
            db_sess = db_session.create_session()
            is_not_log = db_sess.query(User).filter(User.email == form_sing_up.email.data).first()
            if is_not_log is not None:
                return render_template('login.html', form_sing_up=form_sing_up,
                                       message_sing_up='Пользователь с такой почтой уже существует')
            user = User(name=form_sing_up.name.data, email=form_sing_up.email.data)
            user.set_password(form_sing_up.password.data)
            db_sess.add(user)
            db_sess.commit()
            login_user(user, remember=True)
            if send_token(form_sing_up.email.data):
                return render_template('confirm_email.html', email=form_sing_up.email.data)
            else:
                return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                       message_sing_up='Не удалось отправить сообщение с подверждением.')

        except Exception as e:
            print(f'Error sing_up email:{form_sing_up.email.data}. Error:{e}')
    return render_template('sing-up-for-mobile.html', form_sing_up=form_sing_up)


@app.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        return redirect('/')
    email = confirm_token(token)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db_sess.add(user)
        db_sess.commit()
        send_email(user.email, 'Добро пожаловать в DragoSearch', 'Добро пожаловать в DragoSearch!', 'text')
    return redirect('/')


@app.route('/login/authorized')
def yandex_oauth():
    if request.args.get('code', False):
        # Если скрипт был вызван с указанием параметра "code" в URL,
        # то выполняется запрос на получение токена
        print(request.args)
        print(request.data)
        data = {
            'grant_type': 'authorization_code',
            'code': request.args.get('code'),
            'client_id': os.environ.get('YANDEX_CLIENT_ID'),
            'client_secret': os.environ.get('YANDEX_CLIENT_SECRET')
        }
        data = urlencode(data)
        # Токен необходимо сохранить для использования в запросах к API Директа
        access_token = post('https://oauth.yandex.ru/token', data).json()['access_token']
        ya_user_info = get(f'https://login.yandex.ru/info?format=json&oauth_token={access_token}').json()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email==ya_user_info['default_email']).first()
        if user is None:
            new_user = User(name=ya_user_info['real_name'], email=ya_user_info['default_email'], is_confirmed=True,
                            confirmed_on=datetime.datetime.now())
            db_sess.add(new_user)
            db_sess.commit()
            login_user(new_user, remember=True)
            send_email(new_user.email, 'Добро пожаловать в DragoSearch',
                       'Добро пожаловать в DragoSearch! '
                       'Мы рады что вы теперь с нами!\n---\nСистемма поздравлений DragoSearch!', 'text')
            return redirect('/')
        login_user(user, remember=True)
        send_email(user.email, 'Новый вход на DragoSearch',
                   f'Вы вошли в DragoSearch '
                   f'в {datetime.datetime.now().strftime("%A %d-%B-%y %H:%M:%S")} '
                   f'\n---\nС уважением отдел оповещений DragoSearch', 'text')
        return redirect('/')
    else:
        # Если скрипт был вызван без указания параметра "code",
        # то пользователь перенаправляется на страницу запроса доступа
        return redirect('https://oauth.yandex.ru/' + "authorize?response_type=code&client_id={}".format(
            os.environ.get('YANDEX_CLIENT_ID')))


if __name__ == '__main__':
    # храним базы данных в папке .data для безопастности данных в glitch
    db_session.global_init('.data/news.db')
    app.run()