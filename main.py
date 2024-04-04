from flask import Flask, render_template
from data import db_session
from data.users import User
from data.news import News

app = Flask(__name__)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != 1)
    return render_template('news.html', news=news)

@app.route('/login')
def login():
    return render_template('login.html')


def craete_news():
    db_sess = db_session.create_session()
    news = News(title="Первая моя новость", content="Я так рад что это моя первый пост!!!!!",
            user_id=2, is_private=False)
    db_sess.add(news)
    db_sess.commit()


if __name__ == '__main__':
    db_session.global_init('db/news.db')
    craete_news()
    app.run(host='127.0.0.1', port=8080)
