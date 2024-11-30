from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/register')
def register():
    requestapp = request.args
    print(requestapp)
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/subscribe')
def login():
    return render_template("checkout.html")

@app.route('/')
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port='8000', debug=True)
