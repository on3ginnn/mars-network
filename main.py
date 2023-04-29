from flask import Flask, render_template, redirect, abort, request
from werkzeug.utils import secure_filename
import os
from data import db_session, jobs_api
from data.users import User
from data.news import News
import datetime
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource


app = Flask(__name__)
api = Api(app)
app.config['IMG_FOLDER'] = 'static/img'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Профиль личный
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'GET':
        return render_template('profile.html', user=current_user)


# Профиль чужой
@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def writer_profile(id):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()

        return render_template('profile.html', user=user)


def main():
    db_session.global_init('db/mars_network.db')
    app.run(port=5000, host='127.0.0.1')


# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )

        avatar = request.files['avatar']
        if avatar:
            filename = secure_filename(avatar.filename)
            avatar_path = os.path.join(app.config['IMG_FOLDER'], filename)
            avatar.save(avatar_path)
            user.avatar = filename

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# Редактирование профиля
@app.route('/register/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    form = RegisterForm()
    if request.method == "GET":
        if current_user:
            form.email.data = current_user.email
            form.password.data = current_user.hashed_password
            form.surname.data = current_user.surname
            form.name.data = current_user.name
            form.age.data = current_user.age
            form.position.data = current_user.position
            form.speciality.data = current_user.speciality
            form.address.data = current_user.address
        else:
            abort(404)
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if current_user:
            # Редактирование аватарки
            avatar = request.files['avatar']
            if avatar:
                filename = secure_filename(avatar.filename)
                avatar_path = os.path.join(app.config['IMG_FOLDER'], filename)
                avatar.save(avatar_path)
                current_user.avatar = filename
            # Редактирование других данных профиля пользователя
            current_user.email = form.email.data
            current_user.surname = form.surname.data
            current_user.name = form.name.data
            current_user.age = form.age.data
            current_user.position = form.position.data
            current_user.speciality = form.speciality.data
            current_user.address = form.address.data
            current_user.modified_date = datetime.datetime.now()
            current_user.set_password(form.password.data)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/profile')
        else:
            abort(404)
    return render_template('register.html', title='Редактирование профиля', form=form)


# Главная страница
@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template("index.html", news=news)


# Добавить новость
@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


# Редактирование новости
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


# Удаление новости
@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
