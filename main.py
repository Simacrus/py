from flask import Flask, render_template, request, flash, session, redirect, url_for
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql.cursors


app: Flask = Flask(__name__)
mysql = MySQL()


app.config['SECRET_KEY'] = 'very secret'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'magaz'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
        login = request.form['login']
        password = request.form['password']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * from user WHERE login = %s', (login))
        user = cursor.fetchone()
        if user:
            flash('Такой поль-тель есть')
        else:
            cursor.execute('INSERT INTO user (login, password) VALUES (%s, %s)', (login, generate_password_hash(password)))
            conn.commit()
            return redirect(url_for('log'))
    return render_template('reg.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
        login = request.form['login']
        password = request.form['password']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * from user WHERE login = %s',  (login))
        user = cursor.fetchone()
        if user:
            password_check = user['password']
            if check_password_hash(password_check,password):
                session['login_in'] = True
                session['login'] = user['login']
                session['id_user'] = user['id_user']
                return redirect(url_for('get_tovar'))
        else:
            flash('Неправильный логин или пароль!')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('login_in', None)
    session.pop('id_user', None)
    session.pop('login', None)
    return render_template('login.html')


@app.route('/tovar', methods=['GET'])
def get_tovar():
    if 'login_in' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        user = session['id_user']
        cursor.execute('SELECT id_tovar, name, description, cost FROM tovar WHERE id_user = %s',(user))
        tovar = cursor.fetchall()
        conn.commit()
        return render_template('tovar.html', tovar=tovar)
    else:
        flash('Войдите')
        return render_template('index.html')


@app.route('/tovar', methods=['POST'])
def add_tovar():
    name = request.form['name']
    description = request.form['description']
    cost = request.form['cost']
    user = session['id_user']
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('INSERT INTO tovar(name, description, cost, id_user) VALUES (%s, %s, %s, %s)', (name, description, cost, user))
    conn.commit()
    return redirect(url_for('get_tovar'))


if __name__ == '__main__':
    app.run(debug=True)
