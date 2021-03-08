from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "<html><body><h1>Hello Search Trend</h1></body></html>\n"