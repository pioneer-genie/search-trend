from flask import Flask, jsonify, render_template
from pymongo import MongoClient
import Crawler_DC
import json

LOCAL_DEBUG = True

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

if (LOCAL_DEBUG):
    mongo_uri = "mongodb://localhost:27017/"
else:
    mongo_uri = "mongodb://hgj:FK1JcByAZvIBAShLDW5Ug4XG7GcorrtxKH7qBafVqdIhCRNPUPPWkKWnQ3tv1ccuaB117zAYbNfcsOpYMqIJIQ==@hgj.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@hgj@"

crawler = Crawler_DC.Crawler_DC()

@app.route("/")
def hello():
    return "<html><body><h1>Hello Search Trend</h1></body></html>\n"

@app.route("/execute")
def execute():
    added_list = crawler.execute()
    mongo_insert_dc(added_list)

    return "<html><body><h1>Executed</h1></body></html>"

@app.route("/get")
def get():
    jsonfiles = json.loads(crawler.getData().to_json(orient='records'))
    return jsonify(jsonfiles)


@app.route("/get_table")
def get_table():
    df = crawler.getData()
    return render_template('get_table.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/mongo_select', methods=['GET'])
def mongo():
    client = MongoClient(mongo_uri)
    db = client.content
    collection = db.dc
    results = collection.find()
    client.close()
    return render_template('mongo.html', data=results)

@app.route('/mongo_insert')
def mongo_insert():
    client = MongoClient(mongo_uri)
    db = client.test
    collection = db.testCollection
    collection.insert({"name":"name", "content":"content"})
    client.close()
    return "<html><body><h1>Inserted</h1></body></html>"

def mongo_insert_dc(para):
    client = MongoClient(mongo_uri)
    db = client.content
    collection = db.dc

    insert_cnt = 0
    if (type(para) is list):
        insert_cnt = collection.insert_many(para)

    if (type(para) is dict):
        insert_cnt = collection.insert(elem)

    client.close()
    return "<html><body><h1>{0} rows Inerted</h1></body></html>".format(insert_cnt)

if __name__ == "__main__":
    app.run()