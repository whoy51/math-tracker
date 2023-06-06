from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, studentid TEXT, name TEXT)")
conn.commit()
cur.close()

password = '12345678'


def generateRandomAccessKey():
    import random
    import string
    global password
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))


generateRandomAccessKey()





class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired(), Length(min=4, max=80)])
    studentid = StringField('Student ID', validators=[InputRequired(), Length(min=7, max=7)])
    key = StringField('Access Key', validators=[InputRequired(), Length(min=8, max=8)])

    def is_password(form, field):
        if field.data != password:
            raise ValidationError('Wrong access key')
    submit = SubmitField('Sign Up')


class ChangePasswordForm(FlaskForm):
    submit = SubmitField('Change Password')


class SQLStatementForm(FlaskForm):
    sqlstatement = StringField('SQL Statement', validators=[InputRequired()])
    submit = SubmitField('Submit')

# SELECT id FROM students WHERE name = '9258830)
@app.route('/', methods=['GET', 'POST'])
def index():  # put application's code here
    if request.method == 'GET':
        return render_template('index.html', form=RegisterForm())
    if request.method == 'POST':
        name = request.form['name']
        studentid = request.form['studentid']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO students (studentid, name) VALUES (?, ?)", (studentid, name))
        conn.commit()
        cur.close()
        return redirect(url_for('debug'))


@app.route('/debug', methods=['GET', 'POST'])
def sql():
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM students")
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


@app.route('/clear')
def clear():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE students")
    cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, studentid TEXT, name TEXT)")
    conn.commit()
    rows = cur.fetchall()
    cur.close()
    print(str(rows))
    return str(rows)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return render_template('admin.html', password=password, form=ChangePasswordForm())
    if request.method == 'POST':
        generateRandomAccessKey()
        print(password)
        return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
