from flask import Flask, render_template, request, redirect, url_for, flash
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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()
    conn.close()
    return render_template("index.html", notes=notes)


@app.route("/add", methods=["POST"])
def add_note():
    content = request.form.get("content")
    if content:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (%s)", (content,))
        conn.commit()
        conn.close()
        flash("Note added successfully!", "success")
    else:
        flash("Note content cannot be empty.", "warning")
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
