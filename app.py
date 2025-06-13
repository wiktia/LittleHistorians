from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def logowanie():
    return render_template("logowanie.html")

@app.route("/start", methods=["POST"])
def start_quiz():
    name = request.form.get("name")
    avatar = request.form.get("avatar")
    return render_template("test2.html", name=name, avatar=avatar)

@app.route("/startscreen")
def startscreen():
    return render_template("startscreen.html")

@app.route('/puzzle')
def puzzle():
    return render_template("puzzle.html")
@app.route("/endscreen")
def endscreen():
    return render_template("endscreen.html")

@app.route("/text_to_image")
def text_to_image():
    return render_template("text_to_image.html")

@app.route("/timeline")
def timeline():
    return render_template("timeline.html")

    

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

if __name__ == "__main__":
    app.run(debug=True)