import psycopg2
from psycopg2 import sql
import bcrypt
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "career"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
}

def init_db():
    db_name = "career"
    try:
        connection = connect_db()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
                exists = cursor.fetchone()

                if not exists:
                    cursor.execute(f"CREATE DATABASE {db_name};")
                    print(f"Database '{db_name}' created successfully!")
                else:
                    print(f"Database '{db_name}' already exists.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()

def connect_db():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except psycopg2.Error as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

def initialize_table():
    create_tables_query = """
    CREATE TABLE IF NOT EXISTS role (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        surname VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(200) NOT NULL,
        role_id INT,
            CONSTRAINT fk_role
                FOREIGN KEY (role_id)
                REFERENCES role (id)
                ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        domain TEXT NOT NULL,
        title VARCHAR(255) NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        content TEXT NOT NULL,
        image TEXT,
        CONSTRAINT fk_user
            FOREIGN KEY (user_id)
            REFERENCES users (id)
            ON DELETE CASCADE
    );

    """
    connection = None
    try:
        connection = connect_db()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(create_tables_query)
        logging.info("Users table is ready.")
    except Exception as e:
        logging.error(f"Error initializing table: {e}")
    finally:
        connection.close()

def hash_password(password):
    """Hash a plain-text password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(hashed_password, plain_password):
    """Verify a hashed password against the plain text."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def add_user(name, surname, email, password):
    """Add a new user to the database."""
    insert_query = """
    INSERT INTO users (name, surname, email, password)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    connection = None
    hashed_password = hash_password(password)
    try:
        connection = connect_db()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(insert_query, (name, surname, email, hashed_password))
                user_id = cursor.fetchone()[0]
        return {"id": user_id}, 201
    except psycopg2.IntegrityError:
        connection.rollback()
        return {"error": "Email already registered. Please use a different email."}, 400
    except Exception as e:
        connection.rollback()
        return {"error": str(e)}, 500
    finally:
        connection.close()


def check_user(email, password):
    query = """
    SELECT id, name, surname, password FROM users
    WHERE email = %s;
    """
    connection = None
    try:
        connection = connect_db()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                user = cursor.fetchone()
                print(f"User found: {user}")  # Debugging: Check what is returned by the query

                if user:
                    user_id, name, surname, hashed_password = user

                    # Use bcrypt to check the hashed password
                    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                        return {
                            "message": "Login successful!",
                            "id": user_id,
                            "name": name,
                            "surname": surname,
                        }, 200
                    else:
                        return {"error": "Invalid email or password."}, 401
                else:
                    return {"error": "Invalid email or password."}, 401
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if connection:
            connection.close()

def get_user(user_id):
    connection = None
    try:
        # Connect to the database
        connection = connect_db()
        if not connection:
            return jsonify({"error": "Failed to connect to the database."}), 500

        # Query to select the user by ID
        query = """
        SELECT id, name, surname, email FROM users WHERE id = ' %s';
        """
        cursor = connection.cursor()
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        # Check if user was found
        if user:
            return {
               "id": user[0],
               "name": user[1],
               "surname": user[2],
               "email": user[3]
               }, 200
        else:
            return jsonify({"error": "User not found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    try:
        init_db()
        initialize_table()
        logging.info("Database initialization complete.")
    except Exception as e:
        logging.error(f"Failed to initialize the database: {e}")


