import psycopg2
from psycopg2 import sql
import bcrypt
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "users"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
}

def connect_db():
    """Establish and return a connection to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except psycopg2.Error as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

def initialize_table():
    """Ensure the users table exists in the database."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        surname VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(200) NOT NULL
    );
    """
    connection = None
    try:
        connection = connect_db()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(create_table_query)
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
        return {"message": "User added successfully!", "user_id": user_id}, 201
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
                            "user_id": user_id,
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

