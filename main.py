# import pymysql
from flask import Flask
from flask_mysqldb import MySQL
from flask import jsonify
from flask import flash, request, session
import MySQLdb.cursors
import re
import yaml
from werkzeug import generate_password_hash
import bcrypt
from werkzeug.security import check_password_hash

app = Flask(__name__)

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

app.config['SECRET_KEY'] = '25b8179bb7206d84036ad1f8927c4e8b'

@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    cursor = cur
    rows= cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
    message = {
        'result' : True,
        'data' : rows
    }
    resp = jsonify(message)
    resp.status_code = 200
    return resp

@app.route('/users/<id>')
def usersId(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM users WHERE id=%s", [id])
    if resultValue > 0:
        userDetails = cur.fetchone()
        # check_password_hash(userDetails.password)
        cur.close()
        resp = jsonify(userDetails)
        resp.status_code = 200
        return resp

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form
        name = user['name']
        email = user['email']
        password = user['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cur = mysql.connection.cursor()
        data = (name, email, hash_password)
        cur.execute("INSERT INTO users(name, email, password) VALUES(%s, %s, %s)",data)
        mysql.connection.commit()
        sess=session['name'] = user['name']
        sess2=session['email'] = user['email']
        sessions = (sess, sess2)
        cur.close()
        message = {
            'result' : True,
            'data' : data,
            'message' : 'User added successfully!',
            'session': sessions
        }
        resp = jsonify(message)
        resp.status_code = 200
        return resp
    else:
        return not_found()

@app.route('/update', methods=['GET','PATCH'])
def update_user():
    if request.method == 'PATCH':
        userDetails = request.form
        id = userDetails['id']
        name = userDetails['name']
        email = userDetails['email']
        password = userDetails['password']
        cur = mysql.connection.cursor()
        _hashed_password = generate_password_hash(password)
        data = (name, email, _hashed_password, id)
        cur.execute("UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s", (data[0], data[1], data[2], data[3]))
        mysql.connection.commit()
        cur.close()
        message = {
            'result': True,
            'data': data,
            'message': 'User updated successfully!'
        }
        resp = jsonify(message)
        resp.status_code = 200
        return resp
    else:
        return not_found()

@app.route('/delete/<id>', methods=['GET', 'DELETE'])
def delete_user(id):
    if request.method == "DELETE":
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", [id])
        mysql.connection.commit()
        cur.close()
        resp = jsonify('User deleted Successfully!')
        resp.status_code = 200
        return resp
    else:
        return not_found()

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # user = request.form
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                sess = session['name'] = user['name']
                sess2 = session['email'] = user['email']
                sessions = (sess, sess2)
                message = {
                    'result': True,
                    'message': 'You are logged in!',
                    'session': sessions
                }
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {
                    'result': False,
                    'message': 'Error password and email not match'
                }
                resp = jsonify(message)
                resp.status_code = 404
                return resp
        else:
            message = {
                'result': False,
                'message': 'Error user not found',
            }
            resp = jsonify(message)
            resp.status_code = 404
            return resp
    else:
        return not_found()

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

if __name__ == "__main__":
    app.run(debug=True)
