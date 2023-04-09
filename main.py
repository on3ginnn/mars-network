from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.news import News
from data.departments import Department
import datetime

from forms.jobs import JobsForm
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init('db/mars_explorer.db')
    db_sess = db_session.create_session()
    #
    #
    # user = db_sess.query(User).filter(User.id == 6).first()
    # news = News(title="on3ginnn", content="on3ginnn on3gin nnon3g innnon3gi nnn on3ginnn on3gi nnn on3ginnn")
    # user.news.append(news)
    # db_sess.commit()
    # user = db_sess.query(User).filter(User.id == 6).first()
    # news = News(title="on3ginnnis_private", content="on3ginis_privatenn on3gin nnon3gis_priva te innnon3gi nis_privatenn on3ginnn on3gi is_privatennn on3ginnn",
    #             is_private=True)
    # user.news.append(news)
    # db_sess.commit()

    # departments = db_sess.query(Department).filter(Department.id == 1).first()
    # получить данные о работах по участникам (members) департамента

    # for id in departments.members.split():
    #     print(db_sess.query(Jobs).filter(Jobs.id == 1).first())

    #
    # programmer = User()
    #
    # programmer.name = "evgeny"
    # programmer.surname = "onegin"
    # programmer.age = "16"
    # programmer.position = "programmer"
    # programmer.speciality = "it"
    # programmer.address = "module_5"
    # programmer.email = "on3ginnn@mars.org"
    # programmer.set_password('on3ginnn')
    # db_sess.add(programmer)
    # db_sess.commit()
    #
    # user = db_sess.query(User).filter(User.name == 'Ben').first()
    # job = Jobs(team_leader=2, job="it it it it", work_size=35, collaborators='2 4',
    #            start_date=datetime.datetime.now())
    # user.jobs.append(job)
    # db_sess.commit()
    #
    #
    #
    #
    # department = Department()
    # department.title = "Программирование"
    # department.chief = "Mark Zuckerberg"
    # department.members = '2 5'
    # department.email = "it@email.ru"
    # db_sess = db_session.create_session()
    # db_sess.add(department)
    # db_sess.commit()


    app.run(port=8080, host='127.0.0.1')


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
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)



# @app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()

    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template("index.html", news=news)


@app.route("/")
def index_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()

    return render_template("index_jobs.html", jobs=jobs)


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
    return render_template('news.html', form=form)


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


@app.route('/jobs',  methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs()
        jobs.team_leader = form.team_leader.data
        jobs.job = form.job.data
        jobs.work_size = form.work_size.data
        jobs.collaborators = form.collaborators.data
        jobs.is_finished = form.is_finished.data
        # current_user.jobs.append(jobs)
        # db_sess.merge(current_user)
        db_sess.add(jobs)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', form=form)


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if (current_user.id == 1 or jobs.team_leader == current_user.id) and jobs:
            form.team_leader.data = jobs.team_leader
            form.job.data = jobs.job
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.is_finished.data = jobs.is_finished

        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if (current_user.id == 1 or jobs.team_leader == current_user.id) and jobs:
            jobs.team_leader = form.team_leader.data
            jobs.job = form.job.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('jobs.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()

    if (current_user.id == 1 or jobs.team_leader == current_user.id) and jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
