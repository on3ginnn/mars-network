from flask import Flask, render_template
from data import db_session
from data.users import User
from data.jobs import Jobs
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init('db/mars_explorer.db')

    app.run(port=8080, host='127.0.0.1')


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()

    return render_template("index.html", jobs=jobs)


if __name__ == '__main__':
    main()
