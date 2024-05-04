from flask import Flask, request, render_template_string
import hashlib
import mysql.connector
import pymongo
import json
from sqlalchemy import create_engine
import pandas as pd
app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload File</title>
</head>
<body>
    <h1>Upload file</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <input type="submit" value="upload">
    </form>
</body>
</html>
'''


@app.route('/page3')
def index():
    return render_template_string(HTML)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file in request'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file and file.filename.endswith('.csv'):
        return handle_csv_file(file)
    elif file and file.filename.endswith('.json'):
        return handle_json_file(file)
    else:
        return 'Please upload csv and json file'


def handle_csv_file(file):
    dataframe = pd.read_csv(file)
    hash_object = hashlib.sha256(file.filename.encode())
    hash_hex = hash_object.hexdigest()
    database_name = 'db1' if int(hash_hex, 16) % 2 != 0 else 'db2'
    table_name = file.filename.replace('.csv', '').replace(' ', '_')

    engine = create_engine(f'mysql+pymysql://root:root@localhost/{database_name}')

    try:
        dataframe.to_sql(table_name, con=engine, if_exists='replace', index=False)
    except Exception as e:
        return f"Database error: {e}"

    return f'file "{file.filename}" has been uploaded "{database_name}" into the table "{table_name}" '


def handle_json_file(file):
    content = json.load(file)

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["db1"]
    collection_name = file.filename.replace('.json', '').replace(' ', '_')
    collection = db[collection_name]

    if isinstance(content, dict):
        collection.insert_one(content)
    elif isinstance(content, list):
        collection.insert_many(content)
    else:
        return 'JSON file type is incorrect，please upload a Json file'

    return f'file "{file.filename}" has been uploaded "{collection_name}"'


if __name__ == '__main__':
    app.run(debug=True)
