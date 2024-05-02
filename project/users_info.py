'''
Author: HeroNexus 1528264038@qq.com
Date: 2024-03-17 16:15:03
LastEditors: HeroNexus 1528264038@qq.com
LastEditTime: 2024-03-17 21:30:50
FilePath: \project\users_info.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from flask import Flask
from flask_mysqldb import MySQL
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dsci551'
app.config['MYSQL_DB'] = 'usercrud'

mysql = MySQL(app)

# MongoDB configuration
mongo_client = MongoClient('mongodb://localhost:27017/')  # Update the connection string if needed
mongo_db = mongo_client['usercrud']  # The MongoDB database name
mongo_collection = mongo_db['users']  # The MongoDB collection name


# Insert user info starts
def insert_multiple_users(users_data):
    with app.app_context():

    # Hash the password
        users_to_insert = [
            (users["id"], users["username"], generate_password_hash(users["password"]), users["type"]) for users in users_data]
    
    # Insert new user and check if it is successful
        query = "INSERT INTO users (id, username, hashed_password, type) VALUES (%s, %s, %s, %s)"
        cur = None
        try:
            cur = mysql.connection.cursor()
            cur.executemany(query, users_to_insert)
            mysql.connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if cur: 
                cur.close()
# Insert into MongoDB
        try:
            mongo_collection.insert_many(users_to_insert_mongo)
            print("Users inserted into MongoDB successfully.")
        except Exception as e:
            print(f"An error occurred with MongoDB: {e}")

if __name__ == "__main__":
    users_data = [
    {"id": 1, "username": "user1", "password": "password1", "type": "administrator"},
    {"id": 2, "username": "user2", "password": "password2", "type": "administrator"},
    {"id": 3, "username": "user3", "password": "password3", "type": "administrator"},
    {"id": 4, "username": "user4", "password": "password4", "type": "administrator"},
    {"id": 5, "username": "user5", "password": "password5", "type": "administrator"},
    {"id": 6, "username": "user6", "password": "password6", "type": "normal"},
    {"id": 7, "username": "user7", "password": "password7", "type": "normal"},
    {"id": 8, "username": "user8", "password": "password8", "type": "normal"},
    {"id": 9, "username": "user9", "password": "password9", "type": "normal"},
    {"id": 10, "username": "user10", "password": "password10", "type": "normal"},
]
    # Run the script
    insert_multiple_users(users_data)
    print("Users inserted successfully.")