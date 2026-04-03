from flask import Flask, render_template_string
import csv

app = Flask(__name__)

@app.route("/")
def home():
    rows = []
    with open("attendance.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    return render_template_string("""
    <h2>Attendance Dashboard</h2>
    <table border=1>
    <tr><th>Name</th><th>Date</th><th>Minutes</th><th>Status</th></tr>
    {% for row in rows %}
    <tr>
    <td>{{row[0]}}</td>
    <td>{{row[1]}}</td>
    <td>{{row[2]}}</td>
    <td>{{row[3]}}</td>
    </tr>
    {% endfor %}
    </table>
    """, rows=rows)

app.run(host="0.0.0.0", port=5000)