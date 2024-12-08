from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from db import initialize_table, add_user, check_user

app = Flask(__name__)

# Secret key for session management
app.secret_key = "your_secret_key"  # Make sure to change this in production!

# PostgreSQL database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the app with the db instance
initialize_table()
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

@app.route('/subscribe')
def subscribe():
    return render_template("checkout.html")

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
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
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

        # Check user credentials
        result, status_code = check_user(email, password)
        if status_code == 200:
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)












