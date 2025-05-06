from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/api/flask-moods", methods=["GET"])
def get_moods():
    return jsonify({"message": "Flask works! Add your logic here."})

if __name__ == "__main__":
    app.run(port=5000)  
   
import sqlite3

@app.route("/api/mood-stats")
def mood_stats():
    conn = sqlite3.connect("db.sqlite3")  
    cursor = conn.cursor()
    cursor.execute("SELECT mood_type, COUNT(*) FROM journal_mood GROUP BY mood_type")
    results = cursor.fetchall()
    conn.close()  
    return jsonify(dict(results))
