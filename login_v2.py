from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'dsci551'

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dsci551'
app.config['MYSQL_DB'] = 'users_info'

mysql = MySQL(app)

# Login process starts
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, type):
        self.id = id
        self.username = username
        self.type = type

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, type FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(id=user[0], username=user[1], type=user[2])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        type = request.form['type']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, hashed_password, type FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        # redirect to the dashboard if username and password is in the database, with username, type and password matching
        if user and check_password_hash(user[1], password) and user[2] == type:
            user_obj = User(id=user[0], username=username, type=user[2])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        
        # return the error message if user type does not match other information
        if user and check_password_hash(user[1], password) and not user[2] == type:
            return 'User type does not match'
        
        # return the error message if password and username are not correct
        else:
            return 'Invalid username or password'
        
    return render_template('login.html')

# render the dashboard if a user/admin successfully logged in
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# log out from the dashboard if the user/admin click the Log out button
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# get list of databases
@app.route('/get-databases')
@login_required
def get_databases():
    cur = mysql.connection.cursor()
    cur.execute("SHOW DATABASES")
    databases = [db[0] for db in cur.fetchall()]
    cur.close()
    return jsonify(databases)

# get list of tables in a specific database
@app.route('/get-tables/<dbname>')
@login_required
def get_tables(dbname):
    cur = mysql.connection.cursor()
    cur.execute(f"USE {dbname}")
    cur.execute("SHOW TABLES")
    tables = [table[0] for table in cur.fetchall()]
    cur.close()
    return jsonify(tables)

if __name__ == '__main__':
    app.run(debug=True)

