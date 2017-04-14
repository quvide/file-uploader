import random, time, threading, os

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

def filepath(filename):
    return "/files/" + filename

def hashkey(file_id):
    return "file:" + file_id

def invalid_password(password):
    return password not in config["passwords"]

@app.route("/api/password", methods=["POST"])
def password():
    if invalid_password(request.form["secret"]):
        if config["max_time"] >= 1:
            return jsonify({
                "status": 2,
                "max_time": config["max_time"]
            })
        else:
            return err("Invalid password!")
    else:
        return jsonify({
            "status": 0,
            "max_time": config["passwords"][request.form["secret"]]["max_time"]
        })

@app.route("/api/upload", methods=["POST"])
def index():
    max_time = config["max_time"]
    if invalid_password(request.form["secret"]):
        if config["max_time"] < 1:
            return err("Invalid password")
    else:
        max_time = max(config["passwords"][request.form["secret"]]["max_time"], max_time)

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

    f.save(filepath(filename))

    file_id = redis.incr("file_id")
    now = time.time()

    user_time = max_time
    if request.form["time"]:
        user_time = int(request.form["time"])

    redis.zadd("files", now + 60*min(user_time, max_time), file_id)

    key = hashkey(str(file_id))
    redis.hset(key, "filename", filename)

    ip = request.remote_addr
    if "REMOTE_ADDR" in request.environ:
        ip = request.environ["REMOTE_ADDR"]
    elif "X-Real-IP" in request.environ:
        ip = request.environ["X-Real-IP"]
    redis.hset(key, "uploader_ip", ip)

    redis.hset(key, "time", now)
    redis.hset(key, "password", request.form["secret"])

    print("Uploaded {}".format(filename))

    return jsonify({
        "status": 0,
        "uploaded_name": filename
    })

def clean_old_files():
    threading.Timer(5, clean_old_files).start()
    files = redis.zrangebyscore("files", 0, time.time())
    if files:
        print("{} files have expired, removing...".format(len(files)))

    for f in files:
        filename = redis.hget(hashkey(f), "filename")
        redis.zrem("files", f)
        os.remove(filepath(filename))
        print("Removed {}".format(filename))

clean_old_files()
