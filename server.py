from flask import Flask, render_template, request, redirect
from requests import post, get
from data import db_session, giga_api
from data.users import User
from data.news import News
import os
from os.path import join, dirname
from dotenv import load_dotenv
from forms.login import LoginForm
from forms.sing_up import SingUpForm
from forms.fog_password import FogPassword
from forms.set_user_sett import SetSettings
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from email_sender import send_token, send_email
from tokens import confirm_token
import datetime
from urllib.parse import urlencode
from generate_password import generate_password

# Загружаем ключи из .env, т.к glitch скрывает эти ключи от пользователей
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# Загружаем SECURITY_PASSWORD_SALT, он нужен для генерации ссылок подверждения
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
    # Страница доступна только не авторизованных пользователей
    if current_user.is_authenticated:
        return redirect('/')

    form_login = LoginForm()
    form_sing_up = SingUpForm()
    # получение данных с form_login
    if form_login.validate_on_submit() and form_login.submit_login.data:
        try:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form_login.email.data).first()
            if user and user.check_password(form_login.password.data):
                login_user(user, remember=True)
                # отправляем сообщение о входе
                send_email(user.email, 'Новый вход на DragoSearch',
                           f'Вы вошли в DragoSearch '
                           f'в {datetime.datetime.now().strftime("%A %d-%B-%y %H:%M:%S")} '
                           f'\n---\nС уважением отдел оповещений DragoSearch', 'text')
                return redirect('/')
            return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                   message_login='Неверный пароль или почта')
        except Exception as e:
            print(f'Error login email:{form_login.email.data}. Error: {e}')
            return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                   message_login='Произошла не известная ошибка на сервере')
    # получение данных с form_sing_up
    elif form_sing_up.validate_on_submit() and form_sing_up.submit_sing_up.data:
        try:
            db_sess = db_session.create_session()
            is_not_log = db_sess.query(User).filter(User.email == form_sing_up.email.data).first()
            if is_not_log is not None:
                return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                       message_sing_up='Пользователь с такой почтой уже существует')
            if len(form_sing_up.password.data) >= 7:
                user = User(name=form_sing_up.name.data, email=form_sing_up.email.data)
                user.set_password(form_sing_up.password.data)
                db_sess.add(user)
                db_sess.commit()
                login_user(user, remember=True)
                # отправка письма с потверждением
                if send_token(form_sing_up.email.data):
                    return render_template('confirm_email.html', email=form_sing_up.email.data)
                else:
                    return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                           message_sing_up='Не удалось отправить сообщение с подверждением.')
            else:
                return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                       message_sing_up='Пароль должен быть не менее 7 символов.')

        except Exception as e:
            print(f'Error sing_up email:{form_sing_up.email.data}. Error:{e}')
            return render_template('login.html', form_sing_in=form_login, form_sing_up=form_sing_up,
                                   message_sing_up='Произошла не известная ошибка.')

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
                return render_template('sing-up-for-mobile.html', form_sing_up=form_sing_up,
                                       message_sing_up='Пользователь с такой почтой уже существует')
            if len(form_sing_up.password.data) >= 7:
                user = User(name=form_sing_up.name.data, email=form_sing_up.email.data)
                user.set_password(form_sing_up.password.data)
                db_sess.add(user)
                db_sess.commit()
                login_user(user, remember=True)
                if send_token(form_sing_up.email.data):
                    return render_template('confirm_email.html', email=form_sing_up.email.data)
                else:
                    return render_template('sing-up-for-mobile.html', form_sing_up=form_sing_up,
                                           message_sing_up='Не удалось отправить сообщение с подверждением.')
            else:
                return render_template('sing-up-for-mobile.html', form_sing_up=form_sing_up,
                                       message_sing_up='Пароль должен быть не менее 7 символов.')

        except Exception as e:
            print(f'Error sing_up email:{form_sing_up.email.data}. Error:{e}')
            return render_template('sing-up-for-mobile.html', form_sing_up=form_sing_up,
                                   message_sing_up='Произошла не известная ошибка.')

    return render_template('sing-up-for-mobile.html', form_sing_up=form_sing_up)


# Страница востоновления пароля
@app.route('/login/fog-password', methods=['POST', 'GET'])
def fog_password():
    form_fog_pass = FogPassword()
    if form_fog_pass.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form_fog_pass.email.data).first()
        if user is None:
            return render_template('fogot_password.html', form_fog_password=form_fog_pass,
                                   message_fog_password='Мы не нашли пользователя с такой почтой')
        password = generate_password()
        if send_email(user.email, f'Восстановление пароля DragoSearch',
                      f'Вы отправили запрос на генерацию нового пароля\nВот ваш новый пароль:{password}', 'text'):
            user.set_password(password)
            db_sess.commit()
            return render_template('confirm_fog_password.html', email=user.email)
        else:
            return render_template('fogot_password.html', form_fog_password=form_fog_pass,
                                   message_fog_password='Нам не удалось вам отправить письмо')
    return render_template('fogot_password.html', form_fog_password=form_fog_pass)


# страница, которая получает токен потверждения аккаунта
@app.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        return redirect('/')
    email = confirm_token(token)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    # если пользователь с такой почтой есть, то потверждаем
    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db_sess.add(user)
        db_sess.commit()
        send_email(user.email, 'Добро пожаловать в DragoSearch', 'Добро пожаловать в DragoSearch!', 'text')
    return redirect('/')


# страница для работы с Yandex id OAuth
@app.route('/login/authorized')
def yandex_oauth():
    if request.args.get('code', False):
        # Если скрипт был вызван с указанием параметра "code" в URL,
        # то выполняется запрос на получение токена
        data = {
            'grant_type': 'authorization_code',
            'code': request.args.get('code'),
            'client_id': os.environ.get('YANDEX_CLIENT_ID'),
            'client_secret': os.environ.get('YANDEX_CLIENT_SECRET')
        }
        data = urlencode(data)
        # получаем access_token для получения данных пользователя
        access_token = post('https://oauth.yandex.ru/token', data).json()['access_token']
        # получаем данные пользователя из yandex id
        ya_user_info = get(f'https://login.yandex.ru/info?format=json&oauth_token={access_token}').json()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == ya_user_info['default_email']).first()
        if user is None:
            new_user = User(name=ya_user_info['real_name'], email=ya_user_info['default_email'], is_confirmed=True,
                            confirmed_on=datetime.datetime.now(), avatar=ya_user_info['default_avatar_id'],
                            avatar_is_file=False)
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


# страница настроек пользователя
@app.route('/user/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    form = SetSettings()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.name = form.name.data
        if user.email != form.email.data:
            send_email(user.email, 'Изменена почта', f'На вашем аккаунте изменена почта на {form.email.data}', 'text')
            user.email = form.email.data
        if form.avatar.data:
            # загружаем изображение пользователя
            f = form.avatar.data
            user.avatar = f.filename
            user.avatar_is_file = True
            # и сохраняем в static img avatars папку
            os.makedirs('static/img/avatars', exist_ok=True)
            f.save(os.path.join('static/img/avatars', f.filename))
        user.about = form.about.data
        if form.new_password.data:
            if (len(form.new_password.data) < 6 or len(form.repeat_password.data) < 6 or
                    len(form.old_password.data) < 6):
                return render_template('user_settings.html', form=form,
                                       message_error='Пароль должен быть не менее 7 символов')
            if user.check_password(form.old_password.data) and form.new_password.data == form.repeat_password.data:
                user.set_password(form.new_password.data)
                send_email(user.email, 'Изменение пароля', f'Ваш пароль был изменен',  'text')
            else:
                return render_template('user_settings.html', form=form,
                                       message_error='Ошибка не правильный пароль или пароли не совпадают')
        db_sess.commit()
        return redirect('/')
    return render_template('user_settings.html', form=form)


# страница редактирования поста
@app.route('/create_news', methods=['GET', 'POST'])
@login_required
def create_news():
    if current_user.is_confirmed:
        if request.method == 'GET':
            return render_template('news_edit.html')
        elif request.method == 'POST':
            print(request.form)
            if request.form['title'] and request.form['text']:
                db_sess = db_session.create_session()
                file = request.files['image']
                os.makedirs(f'static/img/news', exist_ok=True)
                file.save(os.path.join('static/img/news', file.filename))
                new_post = News(title=request.form['title'], image=file.filename, content=request.form['text'],
                                is_private=False, user_id=current_user.id)
                db_sess.add(new_post)
                db_sess.commit()
                return redirect('/')
            else:
                return render_template('news_edit.html', message='Заполните все поля')
    else:
        return render_template('/')


@app.route('/news/<int:news_id>')
def news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == news_id).first()
    if news:
        news.views += 1
        db_sess.commit()
        return render_template('user_text_post.html', news=news, title=news.title, base_url=os.environ.get('BASE_URL'))


@app.route('/news/ai/<int:news_id>')
def ai300(news_id):
    endpoint = 'https://300.ya.ru/api/sharing-url'
    response = post(
        endpoint,
        json={
            'article_url': f'https://profuse-lateral-aftermath.glitch.me/news/1'
        },
        headers={'Authorization': f'OAuth {os.environ.get("300_AI_TOKEN")}'}
    )
    print(response.json())
    return redirect(response.json()['sharing_url'])


if __name__ == '__main__':
    # храним базы данных в папке .data для безопастности данных в glitch
    db_session.global_init('.data/news.db')
    app.register_blueprint(giga_api.blueprint)
    app.run()
