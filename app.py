from flask import Flask, render_template, send_file
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    df = pd.read_csv("attendance.csv")
    data = df.to_dict(orient='records')

    total = len(data)
    present = sum(1 for i in data if i['Attendance_Status'] == 'PRESENT')
    absent = total - present

    return render_template("index.html", data=data, total=total, present=present, absent=absent)

@app.route('/download')
def download():
    return send_file("attendance.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)