from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from urllib.parse import urlparse
from db import initialize_table, add_user, get_user, check_user, add_post, get_posts
from datetime import date
import os


app = Flask(__name__)

app.secret_key = os.urandom(24)  # This generates a random secret key. You can set it manually.

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

initialize_table()

@app.route("/healthcare")
@app.route("/it")
@app.route("/education")
@app.route("/engineering")
@app.route("/finance")
@app.route("/art-media")
@app.route("/tourism")
def career():
    path = request.path.strip("/")
    slug = path.split("/")[0]
    empty_page = ""
    response, status_code = get_posts(slug)
    if "posts" in response and response["posts"]:
        posts = response["posts"]
    else:
        posts = ""
        empty_page = "../static/images/nopostyet.png"
    return render_template("career.html", curr_dir=request.path[1:].capitalize(), user = session, posts = posts, empty_page = empty_page)
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

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/it/aws')
def aws_demo():
    return render_template("posts.html", user = session, curr_dir = 'It')


@app.route('/post/<crud>', methods=['GET', 'POST'])
def postCrud(crud):
    user_id = session.get('id')

    if request.method == "GET":
        referrer = request.referrer
        if referrer:
            parsed_url = urlparse(referrer)
            referrer_slug = parsed_url.path.split('/')[-1]
        else:
            referrer_slug = '/'

        return render_template("postCrud.html", action=crud.capitalize(), user=session, referrer=referrer_slug)

    if request.method == "POST":
        if not user_id:
            return jsonify({"error": "User is not logged in."}), 401
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.form.get('image')

        referrer_slug = request.form.get('referrer')



        if not all([title, content]):
            return jsonify({"error": "All fields are required."}), 400


        image = request.files['image']

        if image.filename == '':
            return "No file selected", 400

        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))

        if crud == 'add':
            current_date = date.today()

            # Convert to datetime with time set to '00:00:00'
            formatted_date = current_date.strftime('%Y-%m-%d')
            response, status_code = add_post(user_id, referrer_slug, title, formatted_date, content, image.filename)
            if status_code == 201:
                    return redirect(f"/{referrer_slug}")
            else:
                return jsonify({"error": "Failed to add post.", "details": response}), status_code

    return render_template("postCrud.html", action=crud.capitalize(), user=session)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        if role == 'student':
            role_id = 1
        else:
            role_id = 2

        # Validate input data
        if not all([name, email, password, role]):
            return jsonify({"error": "All fields are required."}), 400

        # Call the add_user function
        response, status_code = add_user(name, surname, email, password, role_id)
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











