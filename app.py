from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length
from datetime import date
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, studentid TEXT, name TEXT, "
            "attends INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS times (id INTEGER PRIMARY KEY AUTOINCREMENT, studentid TEXT, time DATE)")
conn.commit()
cur.close()
accesskey = ''


def generateRandomAccessKey():
    import random
    import string
    global accesskey
    accesskey = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))


generateRandomAccessKey()


class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[InputRequired(), Length(min=4, max=80)])
    studentid = StringField('Student ID', validators=[InputRequired(), Length(min=7, max=7)])
    key = StringField('Access Key', validators=[InputRequired(), Length(min=4, max=4)])
    submit = SubmitField('Sign Up')


class ChangePasswordForm(FlaskForm):
    submit = SubmitField('Change Password')


class SQLStatementForm(FlaskForm):
    sqlstatement = StringField('SQL Statement', validators=[InputRequired()])
    submit = SubmitField('Submit')


# SELECT id FROM students WHERE name = '9258830)
@app.route('/', methods=['GET', 'POST'])
def index():  # put application's code here
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('index.html', form=form)
    elif request.method == 'POST' and request.form.get('key') == accesskey:
        name = request.form['name']
        studentid = request.form['studentid']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT attends FROM students WHERE studentid = (?)", [studentid])
        attends = cur.fetchone()
        if attends is not None:
            cur.execute("UPDATE students SET attends = attends + 1 WHERE studentid = (?)", [studentid])
        else:
            cur.execute("INSERT INTO students (studentid, name, attends) VALUES (?, ?, 1)", (studentid, name))
        cur.execute("INSERT INTO times (studentid, time) VALUES (?, ?)", [studentid, date.today().strftime('%m-%d-%Y')])
        conn.commit()
        cur.close()
        return render_template('success.html')
    else:
        print("invalid key")
        return render_template('index.html', form=form, message="Please ask your teacher for a valid access key")


@app.route('/debug', methods=['GET', 'POST'])
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


@app.route('/clear')
def clear():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE students")
    cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, studentid TEXT, "
                "name TEXT, attends INTEGER)")
    cur.execute("DROP TABLE times")
    cur.execute("CREATE TABLE IF NOT EXISTS times (id INTEGER PRIMARY KEY AUTOINCREMENT, studentid TEXT, time DATE)")
    conn.commit()
    rows = cur.fetchall()
    cur.close()
    print(str(rows))
    return str(rows)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT name, attends FROM students")
        rows = cur.fetchall()
        cur.close()
        return render_template('admin.html', password=accesskey, form=ChangePasswordForm(), data=rows)

    if request.method == 'POST':
        generateRandomAccessKey()
        print(accesskey)
        return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
