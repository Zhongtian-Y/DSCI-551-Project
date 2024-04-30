from flask import Flask, request, render_template_string
import hashlib
import mysql.connector
import pymongo
import json
from sqlalchemy import create_engine
import pandas as pd
app = Flask(__name__)

# HTML模板，包含文件上传表单
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
        return '没有文件部分在请求中'

    file = request.files['file']
    if file.filename == '':
        return '没有选择文件'

    if file and file.filename.endswith('.csv'):
        return handle_csv_file(file)
    elif file and file.filename.endswith('.json'):
        return handle_json_file(file)
    else:
        return '请上传CSV或JSON格式的文件'


def handle_csv_file(file):
    dataframe = pd.read_csv(file)
    hash_object = hashlib.sha256(file.filename.encode())
    hash_hex = hash_object.hexdigest()
    database_name = 'db1' if int(hash_hex, 16) % 2 != 0 else 'db2'
    table_name = file.filename.replace('.csv', '').replace(' ', '_')

    # 使用 SQLAlchemy 创建 MySQL 连接
    engine = create_engine(f'mysql+pymysql://root:root@localhost/{database_name}')

    try:
        dataframe.to_sql(table_name, con=engine, if_exists='replace', index=False)
    except Exception as e:
        return f"数据库错误: {e}"

    return f'文件 "{file.filename}" 已上传并插入到数据库 "{database_name}" 的表 "{table_name}" 中'


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
        return 'JSON文件格式不正确，需要是一个对象或对象数组'

    return f'文件 "{file.filename}" 已上传并插入到MongoDB数据库的集合 "{collection_name}" 中'


if __name__ == '__main__':
    app.run(debug=True)
