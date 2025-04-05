import random
import string
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from pathlib import Path
import datetime as dt
import json

from watchml import ECGReader


app = Flask(__name__)


@app.route("/api/")
def api():
    return "api index"


def get_current_file():
    if "file" not in request.files:
        return False
    return request.files["file"]


def register_service(ukey, service_id, service_config):
    service_request_dir = Path("./service_dir") / (
        ukey + dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    )
    if not os.path.exists(service_request_dir):
        os.makedirs(service_request_dir, exist_ok=True)

    service_json = {
        "service_id": service_id,
        "service_config": service_config,
        "service_path": str(service_request_dir),
    }

    json.dump(service_json, open(service_request_dir / "service.json", "w"))


@app.route("/api/upload/ecgs/<ukey>", methods=["POST"])
def upload_file(ukey):
    file = get_current_file()
    if file:
        filename = secure_filename(file.filename)
        user_dir = Path("./user_dir") / ukey
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
        file.save(user_dir / filename)

    register_service(
        ukey, "unzipper", {"user": ukey, "zip_path": str(user_dir / filename)}
    )
    return "ok"


@app.route("/api/ecg/image/<ukey>/<ecg_id>")
def ecg_image(ukey, ecg_id):
    ecg_path = Path("./user_dir") / ukey / "ecgs" / (ecg_id + ".csv")
    image_path = Path("./user_dir") / ukey / "ecgs" / (ecg_id + ".png")
    if not os.path.exists(image_path):
        register_service(ukey, "ecg_image", {"user": ukey, "ecg_path": str(ecg_path)})
        return "ok"
    else:
        print("image exists")
        import base64

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        res = jsonify({"image": encoded_string.decode("utf-8")})
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res


@app.route("/api/ecgs/<ukey>")
def get_ecgs(ukey):
    user_dir = Path("./user_dir") / ukey
    if not os.path.exists(user_dir):
        response = jsonify([])
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    if not os.path.exists(user_dir / "ecgs"):
        response = jsonify([])
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    ecg_file_names = os.listdir(user_dir / "ecgs")

    ecgs = []

    for ecg_file_name in ecg_file_names:
        try:
            ecg = ECGReader.read_ecg_from_file(user_dir / "ecgs" / ecg_file_name)
            ecgs.append(ecg.to_json())

        except Exception as e:
            print(e)

    response = jsonify(ecgs)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/api/userkey")
def get_userkey():
    letters = string.ascii_lowercase
    ukey = "".join(random.choice(letters) for i in range(20))
    res = jsonify(ukey)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res


if __name__ == "__main__":
    app.run("0.0.0.0", port="5000")
