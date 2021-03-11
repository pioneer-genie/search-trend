from flask import Flask, jsonify, render_template
import Crawler_DC
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

crawler = Crawler_DC.Crawler_DC()

@app.route("/")
def hello():
    return "<html><body><h1>Hello Search Trend</h1></body></html>\n"

@app.route("/execute")
def execute():
    crawler.execute()
    return "<html><body><h1>Executed</h1></body></html>"

@app.route("/get")
def get():
    jsonfiles = json.loads(crawler.getData().to_json(orient='records'))
    return jsonify(jsonfiles)


@app.route("/get_table")
def get_table():
    df = crawler.getData()
    return render_template('get_table.html', tables=[df.to_html(classes='data')], titles=df.columns.values)


if __name__ == "__main__":
    app.run()