from flask import Flask, request
from flask_cors import CORS
import sys
from celline.database import NCBI, GSE, GSM
from celline.config import Config, Setting
from celline.data.files import FileManager
import json
exec_path = sys.argv[1]
proj_path = sys.argv[2]

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

Config.initialize(exec_path, proj_path, cmd="interactive")
Setting.initialize()


@app.route('/', methods=["GET"])
def index():
    return "Hello TEST"


@app.route("/addgsm", methods=["GET"])
def addgsm():
    try:
        req = request.args
        id = req.get("id")
        if id is None:
            return "INVALID ID"
        else:
            NCBI.add(id)
            return "SUCESS"
    finally:
        return "SUCESS"


@app.route("/getgsm", methods=["GET"])
def get_child_gsm_in_gse():
    try:
        req = request.args
        id = req.get("id")
        if id is None:
            return "INVALID ID"
        else:
            all_data = NCBI.get_gsms()
            target_gsmid = []
            for gsm in all_data:
                if all_data[gsm].parent_gse_id == id:
                    target_gsmid.append({
                        "gsm_id": gsm
                    })
            return target_gsmid
    finally:
        return "SUCESS"


@app.route("/gses", methods=["GET"])
def get_project_gses():
    with open(f"{Config.EXEC_ROOT}/test.log", mode="w") as f:
        f.writelines(FileManager.read_runs()["gsm_id"].to_list())
    return json.dumps([{
        "runid": d.runid,
        "title": d.title,
        "link": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={d.runid}",
        "summary": d.summary,
        "species": d.species,
        "raw_link": d.raw_link,
        "gsms": d.child_gsm_ids,
        "target_gsms": [id for id in d.child_gsm_ids if id["accession"] in FileManager.read_runs()["gsm_id"].to_list()]
    } for d in GSE.runs])


app.run(port=8000, debug=True)
