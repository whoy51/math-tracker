from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import InputRequired, Length
from datetime import date
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from config import SECRET_KEY
import bcrypt
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
accesskey = ''

conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute("SELECT username FROM teachers")
username = cur.fetchall()
cur.close()

print(username)


def generateRandomAccessKey():
    import random
    import string
    global accesskey
    accesskey = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))


generateRandomAccessKey()


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


class RegisterForm(FlaskForm):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT username, username FROM teachers WHERE admin = FALSE")
    username = cur.fetchall()
    cur.close()

    name = StringField('Full Name', validators=[InputRequired(), Length(min=4, max=80)])
    studentid = StringField('Student ID', validators=[InputRequired(), Length(min=7, max=8)])
    teacher = SelectField('Teacher', choices=username)
    key = StringField('Access Key', validators=[InputRequired(), Length(min=4, max=4)])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT username, username FROM teachers")
    username = cur.fetchall()
    cur.close()

    username = SelectField('Username', choices=username)
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    submit = SubmitField('Submit')


class ChangeAccessKeyForm(FlaskForm):
    change_key = SubmitField('Change Access Key')


class SQLStatementForm(FlaskForm):
    sqlstatement = StringField('SQL Statement', validators=[InputRequired()])
    submit = SubmitField('Submit')


class CreateNewUserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=80)])
    password = StringField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    is_admin = SelectField('Is Admin', choices=[('True', 'True'), ('False', 'False')])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('index.html', form=form)
    elif request.method == 'POST' and request.form.get('key') == accesskey:
        name = request.form['name']
        studentid = request.form['studentid']
        teacher = request.form['teacher']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT attends FROM students WHERE studentid = (?)", [studentid])
        attends = cur.fetchone()
        cur.execute("SELECT time FROM times WHERE studentid = (?)", [studentid])
        time = cur.fetchall()
        print(time)
        print(date.today().strftime("%m-%d-%Y"))
        if time.__len__() > 0 and date.today().strftime("%m-%d-%Y") in time[0]:
            return render_template('index.html', form=form, message="You have already signed in today")
        if attends is not None:
            cur.execute("UPDATE students SET attends = attends + 1 WHERE studentid = (?)", [studentid])
        else:
            cur.execute("INSERT INTO students (studentid, name, teacher, attends) VALUES (?, ?, ?, 1)",
                        (studentid, name, teacher))
        cur.execute("INSERT INTO times (studentid, time) VALUES (?, ?)", [studentid, date.today().strftime('%m-%d-%Y')])
        conn.commit()
        cur.close()
        return render_template('success.html')
    else:
        print("invalid key")
        flash("Please ask your teacher for a valid access key")
        return render_template('index.html', form=form, message="Please ask your teacher for a valid access key")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT username, password FROM teachers WHERE username = (?)", [username])
        user = cur.fetchone()
        cur.close()
        if user is not None:
            if bcrypt.checkpw(password.encode("utf-8"), user[1]):
                user = User(username)
                login_user(user)
                return redirect(url_for('admin'))
        flash('Invalid username or password')

    return render_template('login.html', form=LoginForm())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/debug', methods=['GET', 'POST'])
@login_required
def sql():
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM times")
        rows = cur.fetchall()
        cur.close()
        return render_template('sql.html', form=SQLStatementForm(), row=rows)
    if request.method == 'POST':
        sqlstatement = request.form['sqlstatement']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute(sqlstatement)
        conn.commit()
        row = cur.fetchall()
        cur.close()
        return render_template('sql.html', form=SQLStatementForm(), row=row)


@app.route('/student/<studentid>')
@login_required
def student(studentid):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT id, studentid, time FROM times WHERE studentid = (?)", [studentid])
    rows = cur.fetchall()
    cur.execute("SELECT name FROM students WHERE studentid = (?)", [studentid])
    name = cur.fetchone()[0]
    cur.close()
    return render_template('student.html', data=rows, name=name)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT studentid, name, teacher, attends FROM students")
        rows = cur.fetchall()
        cur.close()
        return render_template('admin.html', password=accesskey, form=ChangeAccessKeyForm(), data=rows,
                               form2=CreateNewUserForm())
    if request.method == 'POST' and 'change_key' in request.form:
        generateRandomAccessKey()
        print(accesskey)
        return redirect(url_for('admin'))
    else:
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form['is_admin']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        if is_admin == 'True':
            cur.execute("INSERT INTO teachers (username, password, admin) VALUES (?, ?, TRUE)", (username, password))
        else:
            cur.execute("INSERT INTO teachers (username, password, admin) VALUES (?, ?, FALSE)", (username, password))
        conn.commit()
        cur.close()
        return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=False)
