from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def logowanie():
    return render_template("logowanie.html")

@app.route("/start", methods=["POST"])
def start_quiz():
    name = request.form.get("name")
    avatar = request.form.get("avatar")
    return render_template("test.html", name=name, avatar=avatar)