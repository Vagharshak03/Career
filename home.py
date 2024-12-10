from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from db import initialize_table, add_user, get_user, check_user
import os


app = Flask(__name__)

app.secret_key = os.urandom(24)  # This generates a random secret key. You can set it manually.

initialize_table()

@app.route("/healthcare")
@app.route("/it")
@app.route("/education")
@app.route("/engineering")
@app.route("/finance")
@app.route("/art-media")
@app.route("/tourism")
def career():
    return render_template("career.html", curr_dir=request.path[1:].capitalize(), user = session)
@app.route('/')
def home():
    if 'id' in session:
        db_user, response = get_user(session['id'])
        session['email'] = db_user['email']
        session['name'] = db_user['name']
        session['surname'] = db_user['surname']
    else:
        user = None
    return render_template("index.html", user = session)


@app.route('/account')
def account():
    return render_template("account.html", user = session)

@app.route('/post/<crud>')
def crud(crud):

    return render_template("crud.html", action=crud.capitalize(), user = session)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate input data
        if not all([name, surname, email, password]):
            return jsonify({"error": "All fields are required."}), 400

        # Call the add_user function
        response, status_code = add_user(name, surname, email, password)
        if status_code == 201:
            session['id'] = response['id']
            return redirect(url_for('home'))
        else:
            flash(response["error"], "danger")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()

        # Validate the presence of email and password
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required."}), 400

        result, status_code = check_user(email, password)
        if status_code == 200:
            session['id'] = result["id"]
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    return render_template("login.html")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)

# PostgreSQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/career'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False











