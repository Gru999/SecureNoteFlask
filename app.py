from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


# Database connection
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}


def get_db_connection():
    return mysql.connector.connect(**db_config)



@app.route("/")
def home():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to see your notes.", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notes WHERE user_id = %s", (user_id,))
    notes = cursor.fetchall()
    conn.close()
    return render_template("index.html", notes=notes)




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
        finally:
            conn.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))



@app.route("/add", methods=["POST"])
def add_note():
    content = request.form.get("content")
    user_id = session.get("user_id")
    if content and user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (content, user_id) VALUES (%s, %s)", (content, user_id))
        conn.commit()
        conn.close()
        flash("Note added successfully!", "success")
    else:
        flash("You must be logged in to add a note.", "warning")
    return redirect(url_for("home"))




@app.route("/delete/<int:note_id>")
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    conn.close()
    flash("Note deleted successfully!", "info")
    return redirect(url_for("home"))



@app.route("/note")
def view_note():
    note_id = request.args.get("note_id")
    if note_id:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        conn.close()
        if note:
            return render_template("note.html", note=note)
    return "Note not found", 404


@app.route('/shared_note')
def shared_note():
    note_id = request.args.get('note_id')

    if not note_id:
        flash('No note ID provided.', 'warning')
        return redirect(url_for('home'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        conn.close()

        if note:
            return render_template('shared_note.html', note=note)
        else:
            flash('Note not found.', 'danger')
            return redirect(url_for('home'))

    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)
