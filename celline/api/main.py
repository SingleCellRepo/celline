from flask import Flask
from flask_cors import CORS
import sys

exec_path = sys.argv[1]
proj_path = sys.argv[2]

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


@app.route('/')
def index():
    return "Hello world"


app.run(port=8000, debug=True)
