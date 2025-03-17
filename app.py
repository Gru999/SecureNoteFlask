from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection
db_config = {
    "host": "",
    "user": "",
    "password": "",
    "database": ""
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
    return redirect(url_for("home"))


@app.route("/delete/<int:note_id>")
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    conn.close()
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

if __name__ == "__main__":
    app.run(debug=True)
