from flask import Flask, request, render_template, redirect, url_for
app = Flask(__name__)

@app.route('/set_session')
def set_session(params):
    session = params
    return redirect(url_for('/'))  # Redirect to another route

@app.route("/healthcare")
@app.route("/it")
@app.route("/education")
@app.route("/engineering")
@app.route("/finance")
@app.route("/art-media")
@app.route("/tourism")
def career():
    parameters = {'curr_dir' : request.path[1:].capitalize()}
    return render_template("career.html", params=parameters)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/add')
def create():
    return render_template("create.html")
#
# @app.route('/edit')
# def edit():
#     return render_template("edit.html")
#
# @app.route('/delete')
# def delete():
#     return render_template("delete.html")


if __name__ == '__main__':
    app.run(port='8000', debug=True)
