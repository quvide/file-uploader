import random, time, threading

from flask import Flask, jsonify, request
app = Flask(__name__)

from redis import StrictRedis as Redis
redis = Redis("redis", decode_responses=True)

import ruamel.yaml as yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

    if not config:
        exit("Missing configuration!")

def err(msg):
    print("err: " + msg)
    return jsonify({
        "status": 1,
        "error": msg
    })

@app.route("/upload", methods=["POST"])
def index():
    if request.form["secret"] not in config["passwords"]:
        return err("Invalid password")

    if "file" not in request.files:
        return err("No file part")

    f = request.files["file"]

    if f.filename == "":
        return err("Empty file")

    if "." not in f.filename:
        return err("No file extension")

    file_ext = f.filename.rsplit(".", 1)[1].lower()
    if file_ext not in config["allowed_extensions"]:
        return err("File extension not allowed!")

    filename = str()
    while True:
        filename = "_"
        for x in range(0, config["filename"]["length"]):
            filename += random.choice(config["filename"]["characters"])

        filename += "." + file_ext

        if redis.zscore("files", filename) == None:
            break

    f.save("/files/{}".format(filename))

    file_id = redis.incr("file_id")
    now = time.time()

    redis.zadd("files", now, file_id)

    hashkey = "file:" + str(file_id)
    redis.hset(hashkey, "filename", filename)
    redis.hset(hashkey, "uploader_ip", request.environ["REMOTE_ADDR"])
    redis.hset(hashkey, "time", now)
    redis.hset(hashkey, "password", request.form["secret"])

    print("Uploaded {}".format(filename))

    return jsonify({
        "status": 0,
        "uploaded_name": filename
    })

def clean_old_files():
    threading.Timer(60, clean_old_files).start()
    n = redis.zremrangebyscore("files", 0, time.time() - config["max_time"])
    print("Cleaned {} files".format(n))

clean_old_files()
