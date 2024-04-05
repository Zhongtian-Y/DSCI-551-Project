
from bson import InvalidDocument
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
app = Flask(__name__)
app.secret_key = 'dsci551'

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Root'
app.config['MYSQL_DB'] = 'usercrud'
mysql = MySQL(app)

# mongodb config
app.config['MONGO_URI'] = 'mongodb://localhost:27017/usercrud' 
mongo = PyMongo(app)
  
mongo_db = mongo.db
users = mongo_db.users 
# collection = db["usercrud"]

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
        if user and password == user[1] and user[2] == type:
            user_obj = User(id=user[0], username=username, type=user[2])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        
        # return the error message if user type does not match other information
        else:
            return jsonify({"message": "User type does not match", "status": "error"}), 500
        
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

#MySQL add user
@app.route("/addUserMysql",methods=["POST"])
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
            return jsonify({"message": "added successful!", "status": "success","code":200}), 200  
        except Exception as e:  
            # error JSON response  
            return jsonify({"message": "Failed to add user: {}".format(e), "status": "error"}), 500  
    else:  
        return jsonify({"message": "request method error", "status": "error"}), 405
#MySQL search user
@app.route("/userListMysql",methods=["POST"])
def userListMysql():
    if request.method == 'POST':
        jsonData = request.get_json()
        pageNum = int(jsonData.get('pageNum'))
        pageSize =int(jsonData.get("pageSize"))
        cur = mysql.connection.cursor()
        offset = (pageNum - 1) * pageSize   
  
        # search user order by ID 
        cur = mysql.connection.cursor()  
        cur.execute("SELECT * FROM users ORDER BY id LIMIT %s OFFSET %s", (pageSize, offset))  
        users = cur.fetchall()  
  
        # convert to dictionary
        user_list = []  
        for row in users:  
            user_dict = {  
                'id': row[0],  
                'username': row[1],  
                'type': row[3]
            }  
            user_list.append(user_dict)  
  
        # JSON response  
        return jsonify({"message":"search successful","status": "success", "data": user_list}), 200  
    else:  
        return jsonify({"status": "error", "message": "request method error"}), 405
#MySQL update user
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
  
        # update in database  
        try:  
            cur = mysql.connection.cursor()    
            update_query = """  
                UPDATE users  
                SET username = %s, type = %s  
                WHERE id = %s  
            """
            # upload  
            cur.execute(update_query, (username, user_type, user_id))  
            mysql.connection.commit()  
  
            return jsonify({"message": "update successful!", "status": "success","code":200}), 200  
  
        except Exception as e:  
            # error response  
            mysql.connection.rollback()  
            return jsonify({"status": "error", "message": str(e)}), 500  
    else:  
        return jsonify({"status": "error", "message": "request method error"}), 405   
#MySql delete user
@app.route("/deleteUser", methods=["POST"])  
def deleteUser():  
    if request.method == 'POST':  
        jsonData = request.get_json()  
        user_id = jsonData.get('id')  
  
        # check user ID 
        if not user_id:  
            return jsonify({"status": "error", "message": "missing user ID？"}), 400  
  
        # delete user data  
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
            # error response  
            mysql.connection.rollback()  
            return jsonify({"status": "error", "message": str(e)}), 500  
    else:  
        return jsonify({"status": "error", "message": "request method error"}), 405
 
#MongoDB add user
@app.route("/addUserMongoDB",methods=["POST"])
def addUserMongoDB():
    # get JSON data 
    user = request.get_json()
    # insert into MongoDB
    result = users.insert_one(user)
    return jsonify({'msg': 'added successful', "code":200})
#MongoDB search user 
@app.route("/userListMongoDB",methods=["POST"])
def userListMongoDB():
    #request JSON data
    json_data = request.get_json()
    pageNum = int(json_data.get('pageNum'))
    pageSize =int(json_data.get("pageSize"))
    skip = (pageNum - 1) * pageSize
        # get data from MongoDB 
    result = users.find().skip(skip).limit(pageSize)  
      
    # convert into dictionary  
    user_list = [  
        {  
            'id': str(row['_id']),
            'username': row['username'],  
            'type': row['type']  
        } for row in result  
    ]  
      
    # total user number  
    total_users = users.count_documents({})
    return jsonify({'msg': 'search successful', "code":200, "data": user_list})
#MongoDB update user
@app.route("/updateUserMongoDB", methods=["POST"])  
def updateUserMongoDB():  
    # request JSON data  
    update_data = request.get_json()  
    user_id = update_data.get('id')
    # Check ID
    if not user_id:  
        return jsonify({'msg': 'missing user ID', "code": 400})  
        
    set_on_match = {k: v for k, v in update_data.items() if k != '_id'}  
    set_on_match1 = {k: v for k, v in set_on_match.items() if k != 'password'} 
    update_operation = {"$set": set_on_match1}  
      
    # update 
    result = users.update_one({"_id": ObjectId(user_id)},  update_operation)
    # check update
    if result.matched_count == 0:  
        return jsonify({'msg': 'missing user ID', "code": 404})  
    elif result.modified_count == 0:  
        return jsonify({'msg': 'update unsuccessful？', "code": 200})  
    else:  
        return jsonify({'msg': 'update successful', "code": 200})
#MongoDB delete user
@app.route("/deleteUserMongoDB", methods=["POST"])  
def deleteUserMongoDB():  
    # request JSON data  
    delete_data = request.get_json()  
    user_id = delete_data.get('id')   
    if not user_id:  
        return jsonify({'msg': 'missing ID', "code": 400})  
  
    # convert user ID to ObjectId  
    try:  
        user_id = ObjectId(user_id)  
    except InvalidDocument:  
        return jsonify({'msg': 'ID invalid', "code": 400})  
  
    # delete 
    result = users.delete_one({"_id": user_id})  
  
    # check delet  
    if result.deleted_count == 0:  
        return jsonify({'msg': 'delete unsuccessful', "code": 404})  
    else:  
        return jsonify({'msg': 'delete successful', "code": 200})
    
# get MongoDB collections
@app.route('/get_data_list',methods=["POST"])
def get_data_list():

    return jsonify({'msg': 'collections found', "code":200, "data": mongo_db.list_collection_names()})

if __name__ == '__main__':
    app.run(debug=True)

