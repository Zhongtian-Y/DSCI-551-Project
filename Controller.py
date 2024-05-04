from bson import InvalidDocument
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import logging
import pymysql
import hashlib
import mysql.connector
import pymongo
import json
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)
app.secret_key = 'dsci551'

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'db1'
mysql = MySQL(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json
    user_value = data.get('type')
    session['user_type'] = user_value
    return jsonify({"status": "success", "received": user_value})


class MongoHandler(logging.Handler):
    def __init__(self, mongo, collection_name, level=logging.NOTSET):
        super().__init__(level=level)
        self.mongo = mongo
        self.collection_name = collection_name

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.mongo.db[self.collection_name].insert_one({"message": log_entry})
        except Exception as e:
            print(f"Failed to log to MongoDB: {e}")


# mongodb config
app.config['MONGO_URI'] = 'mongodb://localhost:27017/usercrud'
mongo = PyMongo(app)
logger.addHandler(MongoHandler(mongo.db, "logs"))

mongo_db = mongo.db
users = mongo_db.users

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, type):
        self.id = id
        self.username = username
        self.type = type


@app.route('/api/logs')
def get_logs():
    logs = mongo.db.logs.find()
    logs_list = list()

    for log in logs:
        log['_id'] = str(log['_id'])
        logs_list.append(log)
    print(logs_list)
    return jsonify(logs_list)


@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, type FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(id=user[0], username=user[1], type=user[2])
    return None


@app.route('/', methods=['GET', 'POST'])
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

        if user and check_password_hash(user[1], password) and user[2] == type:
            user_obj = User(id=user[0], username=username, type=user[2])
            login_user(user_obj)
            session['login'] = True
            session['username'] = username
            session['password'] = password
            session['dbUsername'] = "root"
            session['dbPassword'] = "root"
            return redirect(url_for('dashboard'))

        if user and check_password_hash(user[1], password) and not user[2] == type:
            return 'User type does not match'

        else:
            return 'Invalid username or password'

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    user_type = session.get('user_type')
    if user_type == 'user':
        print('render dashboard_user')
        return render_template('dashboard_user.html')
    else:
        print(user_type)
        print('render dashboard')
        return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('login'))


@app.route('/get-databases')
@login_required
def get_databases():
    cur = mysql.connection.cursor()
    cur.execute("SHOW DATABASES")
    databases = [db[0] for db in cur.fetchall()]
    cur.close()
    return jsonify(databases)


@app.route('/get-tables/<dbname>')
@login_required
def get_tables(dbname):
    cur = mysql.connection.cursor()
    cur.execute(f"USE {dbname}")
    cur.execute("SHOW TABLES")
    tables = [table[0] for table in cur.fetchall()]
    cur.close()
    return jsonify(tables)


@app.route("/addUserMysql", methods=["POST"])
def addUserMysql():
    if request.method == 'POST':
        jsonData = request.get_json()
        username = jsonData.get('username')
        password = jsonData.get('password')
        user_type = jsonData.get('type')
        cur = mysql.connection.cursor()
        sql = "INSERT INTO users (username, hashed_password, type) VALUES (%s, %s, %s)"
        try:
            cur.execute(sql, (username, password, user_type))
            # upload  
            mysql.connection.commit()
            cur.close()
            return jsonify({"message": "added successful!", "status": "success", "code": 200}), 200
        except Exception as e:
            # error JSON response  
            return jsonify({"message": "Failed to add user: {}".format(e), "status": "error"}), 500
    else:
        return jsonify({"message": "request method error", "status": "error"}), 405


@app.route("/userListMysql", methods=["POST"])
def userListMysql():
    if request.method == 'POST':
        jsonData = request.get_json()
        pageNum = int(jsonData.get('pageNum'))
        pageSize = int(jsonData.get("pageSize"))
        tableName = str(jsonData.get("table"))
        offset = (pageNum - 1) * pageSize

        cur = mysql.connection.cursor()
        sql = "SELECT * FROM {0} LIMIT {1} OFFSET {2}".format(tableName, pageSize, offset)
        app.logger.info(sql)
        cur.execute(sql)
        users = cur.fetchall()

        user_list = []
        for row in users:
            user_dict = {
                'id': row[0],
                'username': row[1],
                'type': row[3]
            }
            user_list.append(user_dict)

            # JSON response
        return jsonify({"message": "search successful", "status": "success", "data": user_list}), 200
    else:
        return jsonify({"status": "error", "message": "request method error"}), 405


@app.route("/updateUser", methods=["POST"])
def updateUser():
    if request.method == 'POST':
        jsonData = request.get_json()
        user_id = jsonData.get('id')
        username = jsonData.get('username')
        password = jsonData.get('password')
        user_type = jsonData.get('type')

        # check for necessary data 
        if not all([user_id, username]):
            return jsonify({"status": "error", "message": "missing data"}), 400
        try:
            cur = mysql.connection.cursor()
            update_query = """  
                UPDATE users  
                SET username = %s, type = %s  
                WHERE id = %s  
            """
            cur.execute(update_query, (username, user_type, user_id))
            mysql.connection.commit()

            return jsonify({"message": "update successful!", "status": "success", "code": 200}), 200

        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "request method error"}), 405


@app.route("/deleteUser", methods=["POST"])
def deleteUser():
    if request.method == 'POST':
        jsonData = request.get_json()
        user_id = jsonData.get('id')
        if not user_id:
            return jsonify({"status": "error", "message": "missing user ID？"}), 400

        try:
            cur = mysql.connection.cursor()
            # SQL command 
            delete_query = """  
                DELETE FROM users  
                WHERE id = %s  
            """
            # upload  
            cur.execute(delete_query, (user_id,))
            mysql.connection.commit()

            return jsonify({"message": "delete successful", "status": "success"}), 200

        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "request method error"}), 405


@app.route("/addUserMongoDB", methods=["POST"])
def addUserMongoDB():
    user = request.get_json()
    result = users.insert_one(user)
    return jsonify({'msg': 'added successful', "code": 200})


@app.route("/userListMongoDB", methods=["POST"])
def userListMongoDB():
    json_data = request.get_json()
    pageNum = int(json_data.get('pageNum'))
    pageSize = int(json_data.get("pageSize"))
    skip = (pageNum - 1) * pageSize
    result = users.find().skip(skip).limit(pageSize)
    user_list = [
        {
            'id': str(row['_id']),
            'username': row['username'],
            'type': row['type']
        } for row in result
    ]

    total_users = users.count_documents({})
    return jsonify({'msg': 'search successful', "code": 200, "data": user_list})


@app.route("/updateUserMongoDB", methods=["POST"])
def updateUserMongoDB():
    update_data = request.get_json()
    user_id = update_data.get('id')
    if not user_id:
        return jsonify({'msg': 'missing user ID', "code": 400})

    set_on_match = {k: v for k, v in update_data.items() if k != '_id'}
    set_on_match1 = {k: v for k, v in set_on_match.items() if k != 'password'}
    update_operation = {"$set": set_on_match1}

    result = users.update_one({"_id": ObjectId(user_id)}, update_operation)
    if result.matched_count == 0:
        return jsonify({'msg': 'missing user ID', "code": 404})
    elif result.modified_count == 0:
        return jsonify({'msg': 'update unsuccessful？', "code": 200})
    else:
        return jsonify({'msg': 'update successful', "code": 200})


@app.route("/deleteUserMongoDB", methods=["POST"])
def deleteUserMongoDB():
    delete_data = request.get_json()
    user_id = delete_data.get('id')
    if not user_id:
        return jsonify({'msg': 'missing ID', "code": 400})
    try:
        user_id = ObjectId(user_id)
    except InvalidDocument:
        return jsonify({'msg': 'ID invalid', "code": 400})

    result = users.delete_one({"_id": user_id})

    if result.deleted_count == 0:
        return jsonify({'msg': 'delete unsuccessful', "code": 404})
    else:
        return jsonify({'msg': 'delete successful', "code": 200})


@app.route('/get_data_list', methods=["POST"])
def get_data_list():
    return jsonify({'msg': 'collections found', "code": 200, "data": mongo_db.list_collection_names()})


@app.route('/page3')
def index():
    return render_template('uploadFile.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file in request'

    file = request.files['file']
    if file.filename == '':
        return "Did not select file"

    if file and file.filename.endswith('.csv'):
        return handle_csv_file(file)
    elif file and file.filename.endswith('.json'):
        return handle_json_file(file)
    else:
        return 'Please upload csv or json type files'


def handle_csv_file(file):
    dataframe = pd.read_csv(file)
    hash_object = hashlib.sha256(file.filename.encode())
    hash_hex = hash_object.hexdigest()
    database_name = 'db1' if int(hash_hex, 16) % 2 != 0 else 'db2'
    table_name = file.filename.replace('.csv', '').replace(' ', '_')

    engine = create_engine(f'mysql+pymysql://root:root@localhost/{database_name}')

    try:
        dataframe.to_sql(table_name, con=engine, if_exists='append', index=False)
    except Exception as e:
        return render_template('uploadError.html', message='CSV File format incorrect')

    return redirect(url_for('success', filename=file.filename, collection_name=database_name))


def handle_json_file(file):
    content = json.load(file)
    hash_object = hashlib.sha256(file.filename.encode())
    hash_hex = hash_object.hexdigest()
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    db = client['db1'] if int(hash_hex, 16) % 2 != 0 else client["db2"]
    collection_name = file.filename.replace('.json', '').replace(' ', '_')
    collection = db[collection_name]

    if isinstance(content, dict):
        collection.insert_one(content)
    elif isinstance(content, list):
        collection.insert_many(content)
    else:
        return render_template('uploadError.html', message='JSON File format incorrect')

    return redirect(url_for('success', filename=file.filename, collection_name=collection_name))


@app.route('/success')
def success():
    filename = request.args.get('filename')
    collection_name = request.args.get('collection_name')
    return render_template('uploadSuccess.html', filename=filename, collection_name=collection_name)


@app.route('/databases')
def displayDatabases():
    db = pymysql.connect(host="localhost", user='root', password='root')
    cursor = db.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    cursor.close()
    db.close()
    mongo.db.logs.insert_one({"message": "Display Databases"})
    return render_template("displayDatabases.html", databases=databases)


@app.route('/ManageMyDB', methods=['GET'])
def ManageMyDB():
    mongo.db.logs.insert_one({"message": "Log in success"})
    e = ""
    return render_template("home.html", error=e)


@app.route('/ManageMyDB/logout')
def logout2():
    session.clear()
    mongo.db.logs.insert_one({"message": "Log out success"})
    return redirect(url_for("ManageMyDB"))


@app.route('/execute', methods=['POST'])
def executeSQL():
    if request.method == "POST":
        form = request.form
        try:
            db = pymysql.connect(host="localhost", user='root', password='root',
                                 db=form['database'])
            cursor = db.cursor()
            cursor.execute(form['sqlStatement'])
            data = cursor.fetchall()
            db.commit()
            db.close()
            mongo.db.logs.insert_one({"message": "Execute：" + form['sqlStatement']})
        except Exception as e:
            data = str(e)
            db.close()
        return jsonify(data)


@app.route('/databases/<database>')
def displayTables(database):
    db = pymysql.connect(host="localhost", user='root', password='root')
    cursor = db.cursor()
    cursor.execute("SHOW TABLES FROM " + database)
    tables = cursor.fetchall()
    cursor.close()
    db.close()
    mongo.db.logs.insert_one({"message": f"Display all tables in database: {database}"})
    return render_template("displayTables.html", database=database, tables=tables)


@app.route('/databases/<database>/<table>')
def displayRows(database, table):
    error_message = ""
    try:
        db = pymysql.connect(host="localhost", user='root', password='root', db=database)
        cursor = db.cursor()

        try:
            cursor.execute("SHOW COLUMNS FROM " + table)
            columns = [column[0] for column in cursor.fetchall()]

            cursor.execute("SELECT * FROM " + table)
            rows = cursor.fetchall()
            mongo.db.logs.insert_one({"message": f"Display thedata in table {table} in database :{database} "})
        except Exception as e:
            error_message = "Error fetching data: {}".format(e)
            columns = None
            rows = None
            logger.error("Error fetching data: {}".format(e))
            mongo.db.logs.insert_one({"message": f"Error when display data in {table} of {database}"})
        finally:
            cursor.close()
            db.close()
        return render_template("displayRows.html", database=database, table=table, columns=columns, rows=rows,
                               error=error_message)
    except Exception as e:
        error_message = "Error connecting to database: {}".format(e)
        logger.error("Error connecting to database: {}".format(e))
        mongo.db.logs.insert_one({"message": f"Connect to database: {database} error"})
        return render_template("displayRows.html", database=database, table=table, error=error_message)


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response


@app.route("/addHouse", methods=["POST"])
def addHouse():
    if request.method == 'POST':
        jsonData = request.get_json()
        HouseID = jsonData.get('HouseID')
        PostedOn = jsonData.get('PostedOn')
        BHK = jsonData.get('BHK')
        Rent = jsonData.get('Rent')
        Size = jsonData.get('Size')
        City = jsonData.get('City')
        FurnishingStatus = jsonData.get('FurnishingStatus')
        cur = mysql.connection.cursor()
        sql = "INSERT INTO house_rent_dataset (HouseID,PostedOn, BHK, Rent, Size, City, FurnishingStatus) VALUES (%s,%s, %s, %s, %s, %s, %s)"
        try:
            cur.execute(sql, (HouseID, PostedOn, BHK, Rent, Size, City, FurnishingStatus))
            mysql.connection.commit()
            cur.close()
            return jsonify({"message": "House added successfully!", "status": "success", "code": 200}), 200
        except Exception as e:
            return jsonify({"message": "Failed to add house: {}".format(e), "status": "error"}), 500


@app.route("/houseList", methods=["POST"])
def houseList():
    if request.method == 'POST':
        jsonData = request.get_json()
        pageNum = int(jsonData.get('pageNum'))
        pageSize = int(jsonData.get("pageSize"))
        offset = (pageNum - 1) * pageSize
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM house_rent_dataset ORDER BY HouseID LIMIT %s OFFSET %s", (pageSize, offset))
        houses = cur.fetchall()
        house_list = []
        for row in houses:
            house_dict = {
                'HouseID': row[0],
                'PostedOn': row[1],
                'BHK': row[2],
                'Rent': row[3],
                'Size': row[4],
                'City': row[5],
                'FurnishingStatus': row[6]
            }
            house_list.append(house_dict)
        return jsonify({"message": "Search successful", "status": "success", "data": house_list}), 200


@app.route("/updateHouse", methods=["POST"])
def updateHouse():
    if request.method == 'POST':
        jsonData = request.get_json()
        PostedOn = jsonData.get('PostedOn')
        HouseID = jsonData.get('HouseID')
        BHK = jsonData.get('BHK')
        Rent = jsonData.get('Rent')
        Size = jsonData.get('Size')
        City = jsonData.get('City')
        FurnishingStatus = jsonData.get('FurnishingStatus')
        cur = mysql.connection.cursor()
        update_query = "UPDATE house_rent_dataset SET  PostedOn = %s, BHK = %s, Rent = %s, Size = %s, City = %s, FurnishingStatus = %s WHERE HouseID = %s"
        cur.execute(update_query, (PostedOn, BHK, Rent, Size, City, FurnishingStatus, HouseID))
        mysql.connection.commit()
        return jsonify({"message": "House updated successfully!", "status": "success", "code": 200}), 200


@app.route("/deleteHouse", methods=["POST"])
def deleteHouse():
    if request.method == 'POST':
        jsonData = request.get_json()
        HouseID = jsonData.get('HouseID')
        cur = mysql.connection.cursor()
        delete_query = "DELETE FROM house_rent_dataset WHERE HouseID = %s"
        cur.execute(delete_query, (HouseID,))
        mysql.connection.commit()
        return jsonify({"message": "House deleted successfully", "status": "success"}), 200


@app.route("/NormalList", methods=["POST"])
def normalList():
    if request.method == 'POST':
        jsonData = request.get_json()
        pageNum = int(jsonData.get('pageNum'))
        pageSize = int(jsonData.get("pageSize"))
        tableName = str(jsonData.get("tableName"))
        dbName = str(jsonData.get("dbName"))

        offset = (pageNum - 1) * pageSize
        sql_query = "SELECT * FROM `{}` LIMIT %s OFFSET %s".format(tableName)
        cur = mysql.connection.cursor()
        cur.execute(f"USE {dbName};")
        cur.execute(sql_query, (pageSize, offset))
        table_rows = cur.fetchall()

        columns = [desc[0] for desc in cur.description]
        table_list = []
        for row in table_rows:
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            table_list.append(row_dict)

        return jsonify({"message": "Search successful", "status": "success", "data": table_list}), 200


if __name__ == '__main__':
    app.run(debug=True)
